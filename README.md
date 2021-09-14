# pixiv-rank
该项目主要将pixiv的每日推荐图片用于个人的壁纸上。

由于插画使用时**均未获得画师授权**，因此在公开场合使用可能会造成**版权侵犯**，请注意！


## 展示
<https://pixiv.shojo.cn>


## 请求方式
> https://pixiv.shojo.cn/api/random-pic

*请求方式：GET*

**url参数：**

| 参数名  | 类型 | 内容        | 参数                              | 必要性 | 备注 |
| ------ | ---- | ----------- | -------------------------------- | ----- | --- |
| type   | str  | 图片形式     | pc, phone, square, all(默认)     | 可选   | 分别是横图、竖图、和方图 |
| sex    | num  | sexual      | 0(默认), 1                       | 可选   | pixiv提供的信息过滤可能暴露的图片 |
| format | str  | 返回形式     | json(默认), raw                  | 可选   | raw则重定向到图片地址 |
| proxy  | str  | 图片反代链接 | (url)(默认:https://i.pixiv.cat/) | 可选   | 如果有其他参数冲突可使用encodeURIComponent |

**json回复：**

| 字段名 | 类型 | 内容 | 备注 |
| ----- | ---- | ---- | --- |
| illust_id | num | 插画id |
| rank | num | 排名 |
| title | str | 标题 | unicode编码 |
| upload_timestamp | num | 上传时间 | 上传时间戳 |
| url | str | 图片链接 | 带proxy的链接 |
| user_id | num | 用户id |
| user_name | str | 用户名 |

**raw重定向回复：**

返回头里包含`illust_id`和`user_id`，含义同上


## 感谢
图片反代：<https://pixiv.cat> 
