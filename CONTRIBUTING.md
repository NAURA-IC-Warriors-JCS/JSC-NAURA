# Contributing to DRL-d

感谢您对DRL-d项目的贡献兴趣！

## 开发环境设置

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/DRL-d.git
cd DRL-d
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装依赖：
```bash
pip install -e .[dev]
```

## 代码规范

- 使用Black进行代码格式化
- 使用flake8进行代码检查
- 使用mypy进行类型检查
- 编写单元测试

## 提交流程

1. Fork项目
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add some feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建Pull Request

## 测试

运行测试：
```bash
pytest tests/
```

运行覆盖率测试：
```bash
pytest --cov=src tests/
```

## 文档

更新文档请修改`docs/`目录下的相关文件。