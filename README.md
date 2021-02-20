# micorBlog
Simple micro blog

简易微博

功能概述：

    用户关注：
        用redis set结构，将关注的用户sadd到follow_id集合中，并将被关注的用户sadd到beNotice_id集合中
        
    个人主页：
        展示个人关注的用户，可能认识的人，用sdiff求出两个用户关注的差集，关注人发的微博，取出blog_id中的id
        
    浏览记录：
        用redis list结构，将浏览过的微博lpush到history_id列表中设置过期时间一周
        
    发微博：
        将发布的微博存入mysql，便利beNotice_id集合，将发布微博的id lpush到每个人的blog_id
        
    浏览次数：
        每个用户进入一个微博的主页，incr browse_id 展示浏览次数
        
    点赞：
        用redis set结构，将点赞的用户id sadd到give_id集合,用sunion求出两个用户的交集，只显示点赞用户中我关注的
        
    评论：
        将评论存入mysql



