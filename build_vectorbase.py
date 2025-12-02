"""
构建PDF向量数据库脚本

功能：
- 扫描 pdfs 目录下的所有 PDF 文件
- 逐个处理所有 PDF，将所有内容添加到同一个向量数据库
- 支持强制重建（删除现有数据库，重新构建）

使用方法：
    python build_vectorbase.py              # 增量构建（追加到现有数据库）
    python build_vectorbase.py --rebuild    # 强制重建（删除现有数据库）
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from rich.logging import RichHandler
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

from src.researcher.researcher import Researcher
from src.core.llm_core import SystemError
from src.assets import AssetsInfo

# 配置日志
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="[%H:%M:%S]",
    handlers=[
        RichHandler(
            rich_tracebacks=True,
            markup=True,
            show_time=False,
            show_path=False,
        )
    ],
)

# 设置各个模块的日志级别
logger = logging.getLogger("TestGen")
logger.setLevel(logging.DEBUG)


def find_pdf_files(pdfs_dir: str) -> list[Path]:
    """
    查找指定目录下的所有PDF文件
    
    Args:
        pdfs_dir: PDF文件目录路径
        
    Returns:
        PDF文件路径列表，按文件名排序
    """
    pdf_dir = Path(pdfs_dir)
    if not pdf_dir.exists():
        logger.error(f"PDF目录不存在: {pdfs_dir}")
        return []
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    # 排除 vectorstore 目录（如果有同名PDF文件）
    pdf_files = [f for f in pdf_files if f.is_file()]
    pdf_files.sort(key=lambda x: x.name)
    
    return pdf_files


async def process_all_pdfs(force_rebuild: bool = False):
    """
    处理所有PDF文件，构建向量数据库
    
    Args:
        force_rebuild: 是否强制重建（删除现有数据库）
    """
    logger.info("=" * 80)
    logger.info("PDF向量数据库构建脚本")
    logger.info("=" * 80)
    
    # 查找所有PDF文件
    pdf_files = find_pdf_files(AssetsInfo.pdfs_path)
    
    if not pdf_files:
        logger.error(f"在 {AssetsInfo.pdfs_path} 目录下未找到PDF文件")
        return
    
    logger.info(f"找到 {len(pdf_files)} 个PDF文件：")
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"  {i}. {pdf_file.name}")
    logger.info("")
    
    # 如果强制重建，删除现有向量数据库
    if force_rebuild:
        vectorstore_path = Path(AssetsInfo.pdfs_vector_path)
        if vectorstore_path.exists():
            logger.warning(f"强制重建模式：删除现有向量数据库 {vectorstore_path}")
            import shutil
            shutil.rmtree(vectorstore_path)
            logger.info("现有向量数据库已删除")
        logger.info("")
    
    # 统计信息
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # 处理每个PDF文件
    for i, pdf_file in enumerate(pdf_files, 1):
        pdf_name = pdf_file.name
        pdf_path = str(pdf_file)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"[{i}/{len(pdf_files)}] 开始处理: {pdf_name}")
        logger.info(f"文件路径: {pdf_path}")
        logger.info("=" * 80)
        
        try:
                # 第一个文件且强制重建时，使用force_rebuild=True
                # 否则使用force_rebuild=False（追加到现有数据库）
                is_first = (i == 1)
                should_rebuild = force_rebuild and is_first
                
                if should_rebuild:
                    logger.info("模式: 创建新向量数据库")
                else:
                    logger.info("模式: 追加到现有向量数据库")
                
                logger.info("正在处理，请稍候...")
                
                researcher = Researcher(pdf_path, chunk_size=2000)
                await researcher.process_pdf(force_rebuild=should_rebuild)
                
                success_count += 1
                logger.info("")
                logger.info(f"✓ 成功完成: {pdf_name}")
                
        except SystemError as e:
                # 系统错误，停止整个任务
                failed_count += 1
                failed_files.append((pdf_name, f"系统错误: {str(e)}"))
                logger.error("")
                logger.error(f"✗ 系统错误，停止处理: {pdf_name}")
                logger.error(f"  错误信息: {e}", exc_info=True)
                logger.error("")
                logger.error("=" * 80)
                logger.error("由于系统错误，任务已停止")
                logger.error("=" * 80)
                raise  # 重新抛出，停止整个脚本
                
        except Exception as e:
                # 其他错误（可能是文件读取错误等），记录但继续处理下一个文件
                failed_count += 1
                failed_files.append((pdf_name, str(e)))
                logger.error("")
                logger.error(f"✗ 处理失败: {pdf_name}")
                logger.error(f"  错误信息: {e}", exc_info=True)
                logger.warning("继续处理下一个文件...")
                # 继续处理下一个文件，不中断整个流程
        
        logger.info("")
        logger.info(f"进度: {i}/{len(pdf_files)} 完成")
    
    # 输出统计信息
    logger.info("")
    logger.info("=" * 80)
    logger.info("处理完成统计")
    logger.info("=" * 80)
    logger.info(f"总文件数: {len(pdf_files)}")
    logger.info(f"成功: {success_count}")
    logger.info(f"失败: {failed_count}")
    
    if failed_files:
        logger.warning("")
        logger.warning("失败的文件列表：")
        for pdf_name, error in failed_files:
            logger.warning(f"  - {pdf_name}: {error}")
    
    logger.info("")
    logger.info(f"向量数据库路径: {AssetsInfo.pdfs_vector_path}")
    logger.info("=" * 80)


def main():
    """主函数"""
    # 解析命令行参数
    force_rebuild = "--rebuild" in sys.argv or "-r" in sys.argv
    
    if force_rebuild:
        logger.warning("⚠️  强制重建模式：将删除现有向量数据库并重新构建")
        logger.warning("")
    else:
        logger.info("📝 增量构建模式：将追加到现有向量数据库")
        logger.info("   如需强制重建，请使用: python build_vectorbase.py --rebuild")
        logger.info("")
    
    try:
        asyncio.run(process_all_pdfs(force_rebuild=force_rebuild))
    except KeyboardInterrupt:
        logger.warning("")
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"脚本执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
