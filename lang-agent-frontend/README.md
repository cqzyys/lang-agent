# Lang-Agent

本项目是以LangGraph为底层技术来实现的一个可有限编程的Agent配置平台。
传统的类WorkFlow项目一般只会将上一个节点的输出作为下一个节点的输入，Lang-Agent允许自定义[状态变量]()，可以作用于跨[节点]()的输入、输出，以及[条件边]()的输出，从而实现更精准的控制。


## 技术栈

- [LangGraph](https://langchain-ai.github.io/langgraph/)
- [FastApi](https://fastapi.tiangolo.com/)
- [HeroUI](https://heroui.com)
- [ReactFlow](https://reactflow.dev/)
- [Tailwind CSS](https://tailwindcss.com)


## 安装与启动

本项目分为后端（lang-agent）和前端（lang-agent-frontend）两个子项目。

### lang-agent安装和启动

#### 克隆项目

```bash
git clone 
```

#### 初始化Python环境
后端项目使用poetry进行包管理，poetry的使用方法可以参考[poetry文档](https://python-poetry.org/docs/#installing-manually)。poetry安装完成后，进入项目目录，执行以下命令初始化项目环境。

```bash
poetry install 
```

#### 启动项目

```bash
python -m lang_agent.main
```


### lang-agent-frontend安装和启动

#### 克隆项目

```bash
git clone 
```

#### 安装项目
前端项目使用yarn进行包管理。yarn的使用方法可以参考[yarn文档](https://yarnpkg.com/getting-started/install)。进入项目目录，执行以下命令安装项目依赖包。

```bash
yarn install
```

#### 启动项目

```bash
yarn dev
```

默认访问地址 http://localhost:5173


## 使用说明



## 许可证

本项目使用MIT开源协议。
