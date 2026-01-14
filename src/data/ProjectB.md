## ProjectB项目介绍

本项目旨在打造一款基于量子纠缠理论的“星际宠物领养”小程序，用户可在其中浏览来自半人马座 α 的虚拟萌宠、用火星币支付并实时追踪宠物在虫洞中的快递轨迹。

### 项目成员

- Alex Chen(前端 leader)：邮箱：mailto:alex.chen@example.com 手机号：13900000001
- Bella Wang(前端开发)：邮箱：mailto:bella.wang@example.com 手机号：13900000002
- Carlos Liu(后端开发)：邮箱：mailto:carlos.liu@example.com 手机号：13900000003
- Diana Zhang(Tech Lead)：邮箱：mailto:diana.zhang@example.com 手机号：13900000004
- Ethan Zhao(Project Manager)：邮箱：mailto:ethan.zhao@example.com 手机号：13900000005
- Fiona Wu(QA)：邮箱：mailto:fiona.wu@example.com 手机号：13900000006
- George Li(运维)：邮箱：mailto:george.li@example.com 手机号：13900000007

### 架构图

![架构图](https://jimmy419.github.io/static/ragflowchart.png)

### 技术栈

- 前端：Taro + React + TypeScript
  - 跨端框架：Taro 3（编译至微信小程序、H5、React Native）
  - 组件库：Taro-ui + 自研 Dior Design System
  - 状态管理：Redux Toolkit
  - 网络请求：Taro.request（封装 Axios-like API）
  - 构建工具：Webpack5 + Taro 自动化构建插件
- 后端：Node.js + Express + TypeScript
  - 框架：Express 4
  - 依赖注入：InversifyJS
  - 数据验证：Joi
  - 日志：Winston + Morgan
  - 单元测试：Jest + Supertest
- 数据库：MongoDB 5.x
  - ORM：Mongoose
  - 索引：复合索引 + TTL 索引
  - 备份：阿里云 MongoDB 自动备份策略
- 认证与安全
  - 登录态：JWT（RS256）+ Redis 黑名单
  - 加密：Bcrypt（10 轮）
  - 限流：express-rate-limit
- DevOps & 监控
  - CI/CD：GitHub Actions（支持灰度发布）
  - 质量门禁：SonarQube + ESLint + Prettier
  - 监控告警：阿里云 ARMS + SLS 日志服务
  - 错误追踪：Sentry

### 仓库地址

- [LV 小程序前端仓库地址](https://github.com/christian-lv-couture/sch-diorstar-mpjs)

### 设计

页面设计参考[LV 小程序 Figma](https://www.figma.com/design/jms5LJyv2VKEs9GztXZsiB/DS-WeChat?node-id=19677-24351&t=1I9rNJT41U9DF0Vh-0)

### 日常操作

- 项目部署

  - 前端小程序部署：

    - PPD 环境部署：
      - 从主分支（通常情况下主分支是 main，特殊情况下可能会有变动）拉取最新代码
      - checkout 一个新的分支，分支的命名格式为：feature/ppd-deploy-YYYYMMDD
      - 推送分支到远程仓库
      - 远程 github actions 会自动触发部署到 PPD 环境
    - 生产环境部署：
      - PPD 环境部署成功
      - Tech Lead 在 github 上审批部署到生产环境
      - 审批通过后，github actions 会自动触发部署到生产环境

  - 后端服务部署：
    - PPD 环境部署：
      - 从主分支（通常情况下主分支是 main，特殊情况下可能会有变动）拉取最新代码
      - checkout 一个新的分支，分支的命名格式为：feature/ppd-deploy-YYYYMMDD
      - 推送分支到远程仓库
      - 远程 github actions 会自动触发部署到 PPD 环境
    - 生产环境部署：
      - PPD 环境部署成功
      - Tech Lead 在 github 上审批部署到生产环境
      - 审批通过后，github actions 会自动触发部署到生产环境

- 项目维护
  - 环境监控

    - PPD 环境
      - 监控 PPD 环境的运行状态:我们使用了阿里云的[监控服务](https://cloud.aliyun.com/product/monitor)来监控 PPD 环境的运行状态。
      - 处理 PPD 环境的异常情况:当 PPD 环境出现异常时，我们会及时在[阿里云的监控服务](https://cloud.aliyun.com/product/monitor)上收到通知。并根据通知及时处理异常情况。
    - 生产环境
      - 监控生产环境的运行状态:我们使用了阿里云的[监控服务](https://cloud.aliyun.com/product/monitor)来监控生产环境的运行状态。
      - 处理生产环境的异常情况:当生产环境出现异常时，我们会及时在[阿里云的监控服务](https://cloud.aliyun.com/product/monitor)上收到通知。并根据通知及时处理异常情况。

  - 存储：PPD 和生产的静态文件存储是共用的。都存储在[阿里云的 OSS](https://oss.console.aliyun.com/bucket/oss-cn-shanghai/alcdcdswosuat02-oss/object)上。
