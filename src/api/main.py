"""
GEO Agent FastAPI 主应用
提供基本的 CRUD 接口
"""

import asyncio
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.auth import verify_api_key
from src.api.schemas import (
    AuditRequest,
    AuditResponse,
    AuditListResponse,
    ErrorResponse,
    StatsResponse
)
from src.workflows import GeoWorkflow
from src.models.audit import AuditResult
from src.models.utils import model_to_dict
from src.database.db_operations import insert_one, find_one, find_many, update_one
from src.database.mongodb_pool import get_pool
from utils.logger import logger
from config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化 MongoDB 连接（失败时不阻止应用启动）
    logger.info("Starting GEO Agent API...")
    try:
        await get_pool()
        logger.info("MongoDB connection established")
    except Exception as e:
        logger.warning(f"MongoDB connection failed, but API will continue to run: {str(e)}")
        logger.warning("Some features requiring database may not work until MongoDB is available")
    yield
    # 关闭时清理资源
    logger.info("Shutting down GEO Agent API...")
    # MongoDB 连接池会自动管理，不需要手动关闭


# 创建 FastAPI 应用
app = FastAPI(
    title="GEO Agent API",
    description="自动化审计品牌在生成式引擎中表现的 API",
    version="1.0.0",
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储（简化版本，生产环境应使用数据库）
_audit_cache: dict[str, AuditResult] = {}
_audit_workflows: dict[str, GeoWorkflow] = {}


@app.get("/", tags=["Health"])
async def root():
    """根路径，健康检查"""
    return {
        "service": "GEO Agent API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """健康检查"""
    try:
        pool = await get_pool()
        is_connected = await pool.ping()
        return {
            "status": "healthy" if is_connected else "unhealthy",
            "database": "connected" if is_connected else "disconnected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.post("/detect", response_model=AuditResponse, tags=["Audits"])
async def create_audit(
    request: AuditRequest,
    api_key: str = Depends(verify_api_key)
) -> AuditResponse:
    """
    创建审计任务（生成检测报告）
    
    Args:
        request: 审计请求
        api_key: API Key（通过依赖注入验证）
    
    Returns:
        审计响应
    """
    try:
        logger.info(f"Creating audit for brand: {request.brand_name}, keywords: {request.keywords}")
        
        # 创建工作流
        workflow = GeoWorkflow(
            target_website=request.target_website,
            ground_truth=request.ground_truth
        )
        
        # 异步运行工作流（在后台执行）
        # 这里先返回初始响应，实际执行在后台进行
        from src.models.utils import generate_audit_id
        audit_id = generate_audit_id(request.brand_name)
        
        # 创建初始审计结果
        audit_result = AuditResult(
            audit_id=audit_id,
            brand_name=request.brand_name,
            target_brand=request.target_brand,
            keywords=request.keywords,
            models=[],
            status="running",
            started_at=datetime.utcnow()
        )
        
        # 保存到缓存和数据库
        _audit_cache[audit_id] = audit_result
        _audit_workflows[audit_id] = workflow
        
        # 保存到 MongoDB（如果可用，异步执行，不阻塞响应）
        async def save_to_db():
            try:
                # 快速检查 MongoDB 连接状态，不等待连接
                pool = await get_pool()
                if pool and pool.is_connected:
                    await insert_one(
                        collection_name="audit_results",
                        document=model_to_dict(audit_result),
                        add_timestamp=False
                    )
                else:
                    logger.warning("MongoDB not connected, audit saved to cache only")
            except Exception as e:
                logger.warning(f"Failed to save audit to database: {str(e)}")
        
        # 在后台保存到数据库，不阻塞响应
        asyncio.create_task(save_to_db())
        
        # 在后台运行工作流
        asyncio.create_task(run_audit_workflow(audit_id, request, workflow))
        
        return AuditResponse(
            audit_id=audit_id,
            brand_name=request.brand_name,
            target_brand=request.target_brand,
            keywords=request.keywords,
            status="running",
            geo_score=None,
            started_at=audit_result.started_at,
            completed_at=None,
            error=None
        )
        
    except Exception as e:
        logger.error(f"Failed to create audit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create audit: {str(e)}"
        )


async def run_audit_workflow(
    audit_id: str,
    request: AuditRequest,
    workflow: GeoWorkflow
):
    """在后台运行审计工作流"""
    try:
        logger.info(f"Starting audit workflow: {audit_id}")
        
        # 运行工作流
        result = await workflow.run(
            brand_name=request.brand_name,
            target_brand=request.target_brand,
            keywords=request.keywords,
            audit_id=audit_id
        )
        
        # 更新审计结果
        completed_at = datetime.utcnow()
        
        # 计算持续时间
        audit_result = _audit_cache.get(audit_id)
        if audit_result:
            duration = (completed_at - audit_result.started_at).total_seconds()
        else:
            duration = None
        
        # 构建更新的审计结果
        updated_result = AuditResult(
            audit_id=audit_id,
            brand_name=request.brand_name,
            target_brand=request.target_brand,
            keywords=request.keywords,
            models=[],
            geo_score=result.get("geo_score"),
            status="completed" if not result.get("error") else "failed",
            started_at=audit_result.started_at if audit_result else completed_at,
            completed_at=completed_at,
            duration_seconds=duration,
            error_message=result.get("error")
        )
        
        # 更新缓存
        _audit_cache[audit_id] = updated_result
        
        # 更新数据库
        try:
            await update_one(
                collection_name="audit_results",
                filter={"audit_id": audit_id},
                update={"$set": model_to_dict(updated_result, exclude_unset=True)},
                add_timestamp=False
            )
        except Exception as e:
            logger.warning(f"Failed to update audit in database: {str(e)}")
        
        logger.info(f"Audit workflow completed: {audit_id}")
        
    except Exception as e:
        logger.error(f"Audit workflow failed: {audit_id}, error: {str(e)}")
        # 更新状态为失败
        if audit_id in _audit_cache:
            _audit_cache[audit_id].status = "failed"
            _audit_cache[audit_id].error_message = str(e)


@app.get("/audits/{audit_id}", response_model=AuditResponse, tags=["Audits"])
async def get_audit(
    audit_id: str,
    api_key: str = Depends(verify_api_key)
) -> AuditResponse:
    """
    获取审计结果
    
    Args:
        audit_id: 审计 ID
        api_key: API Key
    
    Returns:
        审计响应
    """
    # 先从缓存查找
    if audit_id in _audit_cache:
        audit_result = _audit_cache[audit_id]
    else:
        # 从数据库查找
        try:
            doc = await find_one(
                collection_name="audit_results",
                filter={"audit_id": audit_id}
            )
            if not doc:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Audit {audit_id} not found"
                )
            from src.models.utils import dict_to_model
            audit_result = dict_to_model(AuditResult, doc)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get audit from database: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get audit: {str(e)}"
            )
    
    return AuditResponse(
        audit_id=audit_result.audit_id,
        brand_name=audit_result.brand_name,
        target_brand=audit_result.target_brand,
        keywords=audit_result.keywords,
        status=audit_result.status,
        geo_score=audit_result.geo_score.overall_score if audit_result.geo_score else None,
        started_at=audit_result.started_at,
        completed_at=audit_result.completed_at,
        error=audit_result.error_message
    )


@app.get("/audits", response_model=AuditListResponse, tags=["Audits"])
async def list_audits(
    skip: int = 0,
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
) -> AuditListResponse:
    """
    列出所有审计结果
    
    Args:
        skip: 跳过的数量
        limit: 返回的数量限制
        api_key: API Key
    
    Returns:
        审计列表响应
    """
    try:
        # 从内存缓存读取（优先使用，因为数据最新）
        cache_audits = list(_audit_cache.values())
        logger.debug(f"Cache has {len(cache_audits)} audits: {[a.audit_id for a in cache_audits]}")
        
        # 同时尝试从 MongoDB 读取（合并数据）
        db_audits_dict = {}
        try:
            pool = await get_pool()
            if pool.is_connected:
                # 添加超时保护，避免阻塞
                try:
                    docs = await asyncio.wait_for(
                        find_many(
                            collection_name="audit_results",
                            filter={},
                            sort=[("started_at", -1)],
                            limit=1000  # 限制最大数量
                        ),
                        timeout=3.0  # 3秒超时
                    )
                    
                    from src.models.utils import dict_to_model
                    
                    for doc in docs:
                        try:
                            audit_result = dict_to_model(AuditResult, doc)
                            # 使用 audit_id 作为 key，用于去重
                            db_audits_dict[audit_result.audit_id] = audit_result
                        except Exception as e:
                            logger.warning(f"Failed to parse audit result from DB: {str(e)}")
                            continue
                except asyncio.TimeoutError:
                    logger.warning("MongoDB query timeout, using cache only")
                except Exception as e:
                    logger.warning(f"MongoDB query failed: {str(e)}, using cache only")
        except Exception as e:
            logger.warning(f"MongoDB connection check failed: {str(e)}, using cache only")
        
        # 合并缓存和数据库的数据（缓存优先级更高，如果有冲突则使用缓存中的版本）
        merged_audits_dict = db_audits_dict.copy()
        for audit_result in cache_audits:
            # 缓存中的数据覆盖数据库中的数据（因为缓存中的数据更新）
            merged_audits_dict[audit_result.audit_id] = audit_result
        
        # 转换为列表并按开始时间倒序排序
        all_audits = list(merged_audits_dict.values())
        all_audits.sort(key=lambda x: x.started_at, reverse=True)
        
        # 应用分页
        paginated_audits = all_audits[skip:skip + limit]
        
        # 转换为响应格式
        audits = []
        for audit_result in paginated_audits:
            audits.append(AuditResponse(
                audit_id=audit_result.audit_id,
                brand_name=audit_result.brand_name,
                target_brand=audit_result.target_brand,
                keywords=audit_result.keywords,
                status=audit_result.status,
                geo_score=audit_result.geo_score.overall_score if audit_result.geo_score else None,
                started_at=audit_result.started_at,
                completed_at=audit_result.completed_at,
                error=audit_result.error_message
            ))
        
        return AuditListResponse(
            audits=audits,
            total=len(all_audits)
        )
        
    except Exception as e:
        logger.error(f"Failed to list audits: {str(e)}", exc_info=True)
        # 发生异常时，至少返回缓存中的数据
        try:
            cache_audits = list(_audit_cache.values())
            cache_audits.sort(key=lambda x: x.started_at, reverse=True)
            paginated_audits = cache_audits[skip:skip + limit]
            
            audits = []
            for audit_result in paginated_audits:
                audits.append(AuditResponse(
                    audit_id=audit_result.audit_id,
                    brand_name=audit_result.brand_name,
                    target_brand=audit_result.target_brand,
                    keywords=audit_result.keywords,
                    status=audit_result.status,
                    geo_score=audit_result.geo_score.overall_score if audit_result.geo_score else None,
                    started_at=audit_result.started_at,
                    completed_at=audit_result.completed_at,
                    error=audit_result.error_message
                ))
            
            logger.warning(f"Returning {len(audits)} audits from cache due to error")
            return AuditListResponse(audits=audits, total=len(cache_audits))
        except Exception as cache_error:
            logger.error(f"Failed to return cache audits: {str(cache_error)}")
        
        # 如果是数据库连接错误，返回空列表而不是错误
        if "MongoDB" in str(e) or "connection" in str(e).lower():
            logger.warning("Database connection error, returning empty list")
            return AuditListResponse(audits=[], total=0)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list audits: {str(e)}"
        )


@app.delete("/audits/{audit_id}", tags=["Audits"])
async def delete_audit(
    audit_id: str,
    api_key: str = Depends(verify_api_key)
) -> dict:
    """
    删除审计结果
    
    Args:
        audit_id: 审计 ID
        api_key: API Key
    
    Returns:
        删除结果
    """
    # 从缓存删除
    if audit_id in _audit_cache:
        del _audit_cache[audit_id]
    if audit_id in _audit_workflows:
        del _audit_workflows[audit_id]
    
    # 从数据库删除
    try:
        from src.database.db_operations import delete_one
        deleted = await delete_one(
            collection_name="audit_results",
            filter={"audit_id": audit_id}
        )
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audit {audit_id} not found"
            )
        
        return {"message": f"Audit {audit_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete audit: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete audit: {str(e)}"
        )


@app.get("/stats", response_model=StatsResponse, tags=["Stats"])
async def get_stats(
    api_key: str = Depends(verify_api_key)
) -> StatsResponse:
    """
    获取统计数据
    
    Args:
        api_key: API Key
    
    Returns:
        统计数据响应
    """
    try:
        # 合并缓存和数据库的数据
        cache_audits = list(_audit_cache.values())
        db_audits_dict = {}
        
        try:
            pool = await get_pool()
            if pool.is_connected:
                docs = await find_many(
                    collection_name="audit_results",
                    filter={},
                    limit=10000
                )
                
                from src.models.utils import dict_to_model
                for doc in docs:
                    try:
                        audit_result = dict_to_model(AuditResult, doc)
                        db_audits_dict[audit_result.audit_id] = audit_result
                    except Exception as e:
                        logger.warning(f"Failed to parse audit result from DB: {str(e)}")
                        continue
        except Exception as e:
            logger.warning(f"MongoDB query failed in stats: {str(e)}")
        
        # 合并数据（缓存优先）
        all_audits_dict = db_audits_dict.copy()
        for audit_result in cache_audits:
            all_audits_dict[audit_result.audit_id] = audit_result
        
        all_audits = list(all_audits_dict.values())
        
        # 计算统计数据
        total_audits = len(all_audits)
        completed_audits = len([a for a in all_audits if a.status == "completed"])
        
        # 计算平均分数
        completed_with_score = [
            a for a in all_audits 
            if a.status == "completed" and a.geo_score and a.geo_score.overall_score is not None
        ]
        average_score = None
        if completed_with_score:
            total_score = sum(a.geo_score.overall_score for a in completed_with_score)
            average_score = total_score / len(completed_with_score)
        
        # 计算品牌数（去重）
        unique_brands = set()
        for audit in all_audits:
            if audit.brand_name:
                unique_brands.add(audit.brand_name)
        total_brands = len(unique_brands)
        
        return StatsResponse(
            total_audits=total_audits,
            completed_audits=completed_audits,
            average_score=average_score,
            total_brands=total_brands
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}", exc_info=True)
        # 发生错误时返回默认值
        return StatsResponse(
            total_audits=0,
            completed_audits=0,
            average_score=None,
            total_brands=0
        )

