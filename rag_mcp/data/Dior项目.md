## DIOR项目介绍
这个项目是用来开发一个基于uni-app的Christian Dior Couture的小程序，用户可以在小程序中查看商品信息、购买商品、查看订单等。

### 项目成员
- Michael(前端leader)：邮箱：mailto:michael@example.com 手机号：13800000000
- Jimmy Jin(前端开发)：邮箱：mailto:jimmy@example.com 手机号：13800001000
- Liangyi(后端开发)：邮箱：mailto:liangyi@example.com 手机号：13800002000
- Ruben(Tech Lead)：邮箱：mailto:ruben@example.com 手机号：13800003000
- Wenjia(Project Manager)：邮箱：mailto:wenjia@example.com 手机号：13800004000
- Jiaxin(QA)：邮箱：mailto:jiaxin@example.com 手机号：13800005000
- Rabah(运维)：邮箱：mailto:rabah@example.com 手机号：13800006000

### 架构图
![架构图](https://jimmy419.github.io/static/ragflowchart.png)


### 技术栈
- 前端：uni-app（Vue.js）
    - 前端框架：uni-app（Vue.js）
    - 前端组件库：uni-ui
    - 前端路由：uni-router
    - 前端请求库：uni-request
- 后端：Node.js、Express
    - 后端框架：Node.js、Express
    - 后端路由：Express Router
- 数据库：MongoDB
- 认证：JWT（JSON Web Tokens）
- CI/CD：GitHub Actions



### 仓库地址
- [DIOR小程序前端仓库地址](https://github.com/christian-dior-couture/sch-diorstar-mpjs)


### 设计
页面设计参考[DIOR小程序Figma](https://www.figma.com/design/jms5LJyv2VKEs9GztXZsiB/DS-WeChat?node-id=19677-24351&t=1I9rNJT41U9DF0Vh-0)


### 日常操作
- 项目部署
    - 前端小程序部署：
        - PPD环境部署：
            - 从主分支（通常情况下主分支是main，特殊情况下可能会有变动）拉取最新代码
            - checkout一个新的分支，分支的命名格式为：feature/ppd-deploy-YYYYMMDD
            - 推送分支到远程仓库
            - 远程github actions会自动触发部署到PPD环境
        - 生产环境部署：
            - PPD环境部署成功
            - Tech Lead在github上审批部署到生产环境
            - 审批通过后，github actions会自动触发部署到生产环境

    - 后端服务部署：
        - PPD环境部署：
            - 从主分支（通常情况下主分支是main，特殊情况下可能会有变动）拉取最新代码
            - checkout一个新的分支，分支的命名格式为：feature/ppd-deploy-YYYYMMDD
            - 推送分支到远程仓库
            - 远程github actions会自动触发部署到PPD环境
        - 生产环境部署：
            - PPD环境部署成功
            - Tech Lead在github上审批部署到生产环境
            - 审批通过后，github actions会自动触发部署到生产环境    

- 项目维护
    - 环境监控
        - PPD环境
            - 监控PPD环境的运行状态:我们使用了阿里云的[监控服务](https://cloud.aliyun.com/product/monitor)来监控PPD环境的运行状态。
            - 处理PPD环境的异常情况:当PPD环境出现异常时，我们会及时在[阿里云的监控服务](https://cloud.aliyun.com/product/monitor)上收到通知。并根据通知及时处理异常情况。
        - 生产环境
            - 监控生产环境的运行状态:我们使用了阿里云的[监控服务](https://cloud.aliyun.com/product/monitor)来监控生产环境的运行状态。
            - 处理生产环境的异常情况:当生产环境出现异常时，我们会及时在[阿里云的监控服务](https://cloud.aliyun.com/product/monitor)上收到通知。并根据通知及时处理异常情况。
    
    - 存储：PPD和生产的静态文件存储是共用的。都存储在[阿里云的OSS](https://oss.console.aliyun.com/bucket/oss-cn-shanghai/alcdcdswosuat02-oss/object)上。