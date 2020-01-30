# 小说爬虫(主要记录)

------

主要解决问题和实现目的：

> * 断点续爬,用Redis去重,Hash方式,不会有误判同时内存占用一般.
> * 分段爬取,每个爬取文件不会搞的太大.
> * 修改CSV文件中可能导致MySQL LOAD INTO语句失效的部分.
> * 可以粗略估算数据量
> * 解决一些采集中的BUG

遇到一些问题:

> * 有些书每个章节连接都是死链.
> * 有些内容里面包含双引号和逗号,不影响标准CSV解释器,但是MySQL LOAD INTO会失效.
> * 有些章节标题竟然是空白的.
> * 如果一次性采集很久,可能文件很大,不利于导入各类数据库或者硬盘保存.

部分数据:

> * CSV文件适用于MySQL导入,无标题,不需要IGNORE.
> * dump.rdb是Redis数据库快照,记录最后一次爬取结果.
> * 储存格式:`id_primary` `id_subset` `title` `chapter_name` `chapter_content`
> * 下载地址:[OneDrive网盘][1]


  [1]: https://hcmcou-my.sharepoint.com/:f:/g/personal/phuong_ntn9_oude_edu_vn/EgV3SkupH7FBgwuEXZP2BYEBtex7HuhwkP275vSin-U0ww?e=2FKFb8 "OneDrive"