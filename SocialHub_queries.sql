/**********************************************
** SocialHub Data Exploration SQL Project
**********************************************/

/*
Project Overview:
- This SQL script is part of the SocialHub Data Exploration project.
- The project explores data related to a fictional social media platform called SocialHub.

About the Database:
- The database schema includes tables for users, photos, likes, comments, follows, tags, and more.
- These tables capture various aspects of user interactions and content on the platform.

Objective:
- The goal of the project is to analyze and derive insights from the SocialHub database using SQL queries.
- The Streamlit web application is built to provide an interactive interface for querying and exploring the data.

File Information:
- Filename: SocialHub_queries.sql
- Author: Darshan Panchal

Instructions:
1. The SQL queries in this script are designed to be run on the SocialHub database.
2. Ensure that the database is properly set up before executing the queries.
3. Customize and adapt the queries based on specific analysis requirements.

Note:
- The database file (SocialHub.db) is not included in this repository to protect sensitive data.
- Please refer to the accompanying Streamlit app for a user-friendly interface to interact with the data.

Thank you for exploring the SocialHub Data Exploration project!
Feel free to reach out for any questions or feedback.
*/

-- [Start of SQL Queries]

#Users with Most Followers
SELECT f.followee_id, u.username, COUNT(*) AS followers_count
FROM follows f
JOIN users u ON f.followee_id = u.id
GROUP BY f.followee_id, u.username
HAVING followers_count = (
	SELECT MAX(followers_count)
	FROM (
		SELECT COUNT(*) AS followers_count
		FROM follows
		GROUP BY followee_id
	) AS max_followers
);
                                      
#Top Users with Most Comments:		
SELECT u.id, u.username, COUNT(c.id) AS comments_count
FROM users u
LEFT JOIN comments c ON u.id = c.user_id
GROUP BY u.id, u.username
HAVING comments_count = (
	SELECT MAX(comments_count)
	FROM (
		SELECT u.id, COUNT(c.id) AS comments_count
		FROM users u
		LEFT JOIN comments c ON u.id = c.user_id
		GROUP BY u.id
	) AS max_comments
);
           
#Users who Have Liked Every Photo:                       
SELECT dl.user_id, u.username
FROM (
	SELECT DISTINCT user_id, photo_id
	FROM likes
) AS dl
JOIN users u ON dl.user_id = u.id
GROUP BY dl.user_id, u.username
HAVING COUNT(DISTINCT dl.photo_id) = (
	SELECT COUNT(DISTINCT id)
	FROM photos
);

#Users Who Have Not Posted Photos:
SELECT u.id, u.username
FROM users u
LEFT JOIN photos p ON u.id = p.user_id
WHERE p.id IS NULL;

#Top 5 users with the Highest Like-to-Comment Ratio:					
SELECT u.id, u.username, COALESCE(SUM(l.likes_count) / NULLIF(CAST(SUM(c.comments_count) AS REAL), 0), 0) AS like_to_comment_ratio
FROM users u
LEFT JOIN (
	SELECT user_id, COUNT(*) AS likes_count
	FROM likes
	GROUP BY user_id
) AS l ON u.id = l.user_id
LEFT JOIN (
	SELECT user_id, COUNT(*) AS comments_count
	FROM comments
	GROUP BY user_id
) AS c ON u.id = c.user_id
GROUP BY u.id, u.username
ORDER BY like_to_comment_ratio DESC
LIMIT 5;

#Users with less people following them than they follow:                       
SELECT u.id, u.username, COUNT(DISTINCT f.follower_id) AS followers_count, COUNT(DISTINCT f.followee_id) AS followees_count
FROM users u
LEFT JOIN follows f ON u.id = f.follower_id OR u.id = f.followee_id
GROUP BY u.id, u.username
HAVING followers_count > followees_count
ORDER BY followers_count DESC;

#Users with Unique Tags:                       
SELECT DISTINCT u.id, u.username
FROM users u
JOIN photos p ON u.id = p.user_id
JOIN photo_tags pt ON p.id = pt.photo_id
JOIN tags t ON pt.tag_id = t.id
WHERE NOT EXISTS (
	SELECT 1
	FROM photo_tags pt2
	JOIN photos p2 ON pt2.photo_id = p2.id
	WHERE u.id != p2.user_id AND pt.tag_id = pt2.tag_id
);

#User's Contribution to Tag Popularity:			
SELECT u.id, u.username, t.tag_name, COUNT(pt.photo_id) AS tag_contribution
FROM users u
JOIN photos p ON u.id = p.user_id
JOIN photo_tags pt ON p.id = pt.photo_id
JOIN tags t ON pt.tag_id = t.id
GROUP BY u.id, u.username, t.tag_name
ORDER BY tag_contribution DESC;

#Users Who Follow Each Other      
SELECT f1.follower_id AS follower_id, u1.username AS follower_name, f1.followee_id AS followee_id, u2.username AS followee_name
FROM follows f1
JOIN follows f2 ON f1.follower_id = f2.followee_id AND f1.followee_id = f2.follower_id
JOIN users u1 ON f1.follower_id = u1.id
JOIN users u2 ON f1.followee_id = u2.id
WHERE f1.follower_id < f1.followee_id;

#Photos with Rank and Like Counts:				
WITH ranked_photos AS (
	SELECT photo_id, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS photo_rank, COUNT(*) AS likes_count
	FROM likes
	GROUP BY photo_id
)
SELECT photo_id, photo_rank, likes_count
FROM ranked_photos
WHERE photo_rank <= 5;

#Photo with the Most Likes:
SELECT l.photo_id, p.image_url, COUNT(*) AS likes_count
FROM likes l
JOIN photos p ON l.photo_id = p.id
GROUP BY l.photo_id, p.image_url
HAVING likes_count = (
	SELECT MAX(likes_count)
	FROM (
		SELECT COUNT(*) AS likes_count
		FROM likes
		GROUP BY photo_id
	) AS max_likes
);

#Average Likes per Photo:                        
SELECT p.photo_id, ph.image_url, AVG(p.likes_count) AS avg_likes_per_photo
FROM (
	SELECT l.photo_id, COUNT(*) AS likes_count
	FROM likes l
	GROUP BY l.photo_id
) AS p
JOIN photos ph ON p.photo_id = ph.id
GROUP BY p.photo_id, ph.image_url;

#Photos with No Likes:					
SELECT p.id, p.image_url
FROM photos p
LEFT JOIN likes l ON p.id = l.photo_id
WHERE l.user_id IS NULL;

#Photos Tagged with Multiple Tags:
SELECT p.id, p.image_url, COUNT(pt.tag_id) AS tags_count
FROM photos p
JOIN photo_tags pt ON p.id = pt.photo_id
GROUP BY p.id
HAVING tags_count > 4;

#TOP 5 Photos with Highest Comments:                       
WITH ranked_photos AS (
	SELECT u.username, p.id AS photo_id, RANK() OVER (ORDER BY COUNT(c.id) DESC) AS photo_rank, COUNT(c.id) AS comments_count
	FROM photos p
	JOIN comments c ON p.id = c.photo_id
	JOIN users u ON p.user_id = u.id
	GROUP BY p.id, u.username
)
SELECT username, photo_id, photo_rank, comments_count
FROM ranked_photos
WHERE photo_rank <= 5;

#Top 5 Photos with Most Engagement:                      
SELECT p.id, p.image_url, (COALESCE(l.total_likes, 0) + COALESCE(c.total_comments, 0)) AS total_engagement
FROM photos p
LEFT JOIN (
	SELECT photo_id, COUNT(*) AS total_likes
	FROM likes
	GROUP BY photo_id
) l ON p.id = l.photo_id
LEFT JOIN (
	SELECT photo_id, COUNT(*) AS total_comments
	FROM comments
	GROUP BY photo_id
) c ON p.id = c.photo_id
ORDER BY total_engagement DESC
LIMIT 5;

#Photos with Similar Tags:                       
SELECT DISTINCT p1.id, p1.image_url, p2.id AS similar_photo_id, p2.image_url AS The_image_url
FROM photos p1
JOIN photo_tags pt1 ON p1.id = pt1.photo_id
JOIN photos p2 ON p1.id < p2.id
JOIN photo_tags pt2 ON p2.id = pt2.photo_id AND pt1.tag_id = pt2.tag_id
GROUP BY p1.id, p1.image_url, similar_photo_id, The_image_url
HAVING COUNT(DISTINCT pt1.tag_id) >= 3;

-- [End of SQL Queries]