# 小说爬虫(主要记录)

------

主要解决问题和实现目的：

> * 断点续爬,用Redis去重,Hash方式,不会有误判同时内存占用一般.
> * 分段爬取,每个爬取文件不会搞的太大.(也会合并一些文件)
> * 修改CSV文件中可能导致MySQL LOAD INTO语句失效的部分.
> * 可以粗略估算数据量
> * 解决一些采集中的BUG
> * 解决上传超时问题

遇到一些问题:

> * 有些书每个章节连接都是死链.
> * 有些内容里面包含双引号和逗号,不影响标准CSV解释器,但是MySQL LOAD INTO会失效.
> * 有些章节标题竟然是空白的.
> * 如果一次性采集很久,可能文件很大,不利于导入各类数据库或者硬盘保存.

性能评估(AWS Fargate 于增量爬取状态下):

> * 采集耗时:~30分钟
> * 上传耗时:< 1分钟
> * 压缩耗时:3 分钟
> * 内存需求:< 256M
> * Redis服务器内存需求: 1.5G
> * 流量消耗:< 10M

数据打包:

> * 本地打包为xz文件,每个文件都在2G以下.(增量会更小)
> * 远程数据为csv文件,每个文件都是原始数据.(偶尔会执行combine.py来合并)

部分数据:

> * CSV文件适用于MySQL导入,无标题,不需要IGNORE.
> * CSV文件不定时增量更新.
> * 储存格式:`id_primary` `id_subset` `title` `chapter_name` `chapter_content`
> * 下载地址:[OneDrive网盘][1]

MySQL导入参考:

```mysql
CREATE TABLE `scrapy` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `id_primary` INT NOT NULL,
    `id_subset` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL DEFAULT '',
    `chapter_name` VARCHAR(200),
    `chapter_content` MEDIUMTEXT,
    `created_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (`id`),
    INDEX `id_subset` (`id_subset`),
    INDEX `id_primary` (`id_primary`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

```mysql
LOAD DATA LOCAL INFILE './yyyy-mm-dd-hh-mm-ss.csv'
REPLACE INTO TABLE scrapy
CHARACTER SET utf8mb4 FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n'
IGNORE 0 LINES 
(`id_primary`,`id_subset`,`title`,`chapter_name`,`chapter_content`)
SET chapter_name = nullif(chapter_name,'无标题');
```


  [1]: https://hcmcou-my.sharepoint.com/:f:/g/personal/phuong_ntn9_oude_edu_vn/EgV3SkupH7FBgwuEXZP2BYEBtex7HuhwkP275vSin-U0ww?e=2FKFb8 "OneDrive"