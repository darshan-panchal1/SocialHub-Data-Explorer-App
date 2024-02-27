import streamlit as st
import pandas as pd
import sqlite3

# Function to run SQL queries
def run_query(query):
    conn = sqlite3.connect('SocialHub.db')
    result = pd.read_sql_query(query, conn)
    conn.close()
    return result

def display_introduction():
    st.sidebar.markdown("### Welcome to SocialHub Data Exploration")
    st.sidebar.markdown("Here's a quick guide to get you started:")
    st.sidebar.markdown("1. **Custom Query**: Enter your own SQL query in the text area.")
    st.sidebar.markdown("2. **Run Custom Query**: Click the 'Run Custom Query' button to execute your query.")
    st.sidebar.markdown("3. **Select Query Type**: Choose a pre-defined query type from the sidebar.")
    st.sidebar.markdown("4. **Run Query**: Click the 'Run User Query' or 'Run Photo Query' button to execute the selected query.")
    st.sidebar.markdown("5. **ERD of Database**: Click the 'ERD of Database' button to view Entity-Relationship Diagram.")
    st.sidebar.markdown("Thank you for exploring!")

# Function to get user input for interactive queries
def interactive_query():
    st.set_page_config(
        page_title="SocialHub Data Exploration 📊",
        layout="wide"
    )

    st.title("SocialHub Data Exploration 📈")
    st.header("Interactive Options")
    
    # Display dropdown selection box for tables
    table_names = run_query("SELECT name FROM sqlite_master WHERE type='table';")['name'].tolist()
    selected_table = st.selectbox("See Tables of Database:", table_names)

    # Checkbox to toggle visibility of the selected table
    toggle_checkbox = st.checkbox("Show Table")

    # Show the selected table when it is chosen and the checkbox is selected
    if selected_table and toggle_checkbox:
        query_result = run_query(f"SELECT * FROM {selected_table};")
        st.subheader(f"{selected_table} Table")
        st.dataframe(query_result)

    # Input for custom query
    custom_query = st.text_area("Enter your SQL query:")
    run_custom_query = st.button("Run Custom Query 🔄")

    # Display custom query result
    if run_custom_query:
        try:
            query_result_custom = run_query(custom_query)
            st.write("Custom Query Result:")
            st.dataframe(query_result_custom)
        except Exception as e:
            st.error(f"Error executing custom query: {e}")

    # Selection box to choose query type
    selected_query_type = st.selectbox('Select a query type:', ['User Query', 'Photo Query'])

    # Button to show/hide database schema image
    show_schema_button = st.button("Click here to see ERD of Database")

    if show_schema_button:
        st.image("0002.jpg", use_column_width=True, caption="Entity-Relationship Diagram")

        # Checkbox to hide database schema image after viewing
        hide_schema_checkbox = st.checkbox("Hide ERD of Database", key="hide_schema")

        if hide_schema_checkbox:
            st.image("", caption="")  
            st.success("Database Schema Image Hidden!")

    # Display query results in the center of the main screen
    with st.container():
        if selected_query_type == 'User Query':
            st.sidebar.subheader("User Queries")
            user_query_type = st.sidebar.selectbox('Select a query type:', ['Users with Most Followers', 'Top Users with Most Comments', 'Users who Have Liked Every Photo','Users Who Have Not Posted Photos','Top 5 users with the Highest Like-to-Comment Ratio','Users with less people following them than they follow','Users with Unique Tags',"User's Contribution to Tag Popularity",'Users Who Follow Each Other'])

            if user_query_type:
                st.sidebar.checkbox("Show Query Info", key=f"user_{user_query_type}")
                run_user_query = st.sidebar.button("Run User Query")

                if run_user_query:
                    if user_query_type == 'Users with Most Followers':
                        query_result_followers = run_query("SELECT f.followee_id, u.username, COUNT(*) AS followers_count FROM follows f JOIN users u ON f.followee_id = u.id GROUP BY f.followee_id, u.username HAVING followers_count = (SELECT MAX(followers_count) FROM (SELECT COUNT(*) AS followers_count FROM follows GROUP BY followee_id) AS max_followers);")
                        st.subheader("Users with Most Followers:")
                        
                        query = """
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
                """

                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_followers)
                        
                    elif user_query_type == 'Top Users with Most Comments':
                            query_result_comments = run_query("SELECT u.id, u.username, COUNT(c.id) AS comments_count FROM users u LEFT JOIN comments c ON u.id = c.user_id GROUP BY u.id, u.username HAVING comments_count = (SELECT MAX(comments_count) FROM (SELECT u.id, COUNT(c.id) AS comments_count FROM users u LEFT JOIN comments c ON u.id = c.user_id GROUP BY u.id) AS max_comments);")
                            st.subheader("Top Users with Most Comments:")
                        
                            query = """
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
            """
                            st.code(query, language='sql')
                            st.subheader("Query Result:")
                     
                            st.dataframe(query_result_comments)

                    elif user_query_type == 'Users who Have Liked Every Photo':
                        query_result_likes = run_query("SELECT dl.user_id, u.username FROM (SELECT DISTINCT user_id, photo_id FROM likes) AS dl JOIN users u ON dl.user_id = u.id GROUP BY dl.user_id, u.username HAVING COUNT(DISTINCT dl.photo_id) = (SELECT COUNT(DISTINCT id) FROM photos);")
                        st.subheader("Users who Have Liked Every Photo:")
                        
                        query = """
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
        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_likes)

                    elif user_query_type == 'Users Who Have Not Posted Photos':
                        query_result_photo = run_query("SELECT u.id, u.username FROM users u LEFT JOIN photos p ON u.id = p.user_id WHERE p.id IS NULL;")
                        st.subheader("Users Who Have Not Posted Photos:")
                        
                        query = """
            SELECT u.id, u.username
            FROM users u
            LEFT JOIN photos p ON u.id = p.user_id
            WHERE p.id IS NULL;
        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_photo)

                    elif user_query_type == 'Top 5 users with the Highest Like-to-Comment Ratio':
                        query_result_ltoc = run_query("SELECT u.id, u.username, COALESCE(SUM(l.likes_count) / NULLIF(CAST(SUM(c.comments_count) AS REAL), 0), 0) AS like_to_comment_ratio FROM users u LEFT JOIN (SELECT user_id, COUNT(*) AS likes_count FROM likes GROUP BY user_id) AS l ON u.id = l.user_id LEFT JOIN (SELECT user_id, COUNT(*) AS comments_count FROM comments GROUP BY user_id) AS c ON u.id = c.user_id GROUP BY u.id, u.username ORDER BY like_to_comment_ratio DESC LIMIT 5;")
                        st.subheader("Top 5 users with the Highest Like-to-Comment Ratio:")
                        
                        query = """
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

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_ltoc)

                    elif user_query_type == 'Users with less people following them than they follow':
                        query_result_ftf = run_query("SELECT u.id, u.username, COUNT(DISTINCT f.follower_id) AS followers_count, COUNT(DISTINCT f.followee_id) AS followees_count FROM users u LEFT JOIN follows f ON u.id = f.follower_id OR u.id = f.followee_id GROUP BY u.id, u.username HAVING followers_count > followees_count ORDER BY followers_count DESC;")
                        st.subheader("Users with less people following them than they follow:")
                        
                        query = """
            SELECT u.id, u.username, COUNT(DISTINCT f.follower_id) AS followers_count, COUNT(DISTINCT f.followee_id) AS followees_count
            FROM users u
            LEFT JOIN follows f ON u.id = f.follower_id OR u.id = f.followee_id
            GROUP BY u.id, u.username
            HAVING followers_count > followees_count
            ORDER BY followers_count DESC;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_ftf)

                    elif user_query_type == 'Users with Unique Tags':
                        query_result_uwu = run_query("SELECT DISTINCT u.id, u.username FROM users u JOIN photos p ON u.id = p.user_id JOIN photo_tags pt ON p.id = pt.photo_id JOIN tags t ON pt.tag_id = t.id WHERE NOT EXISTS (SELECT 1 FROM photo_tags pt2 JOIN photos p2 ON pt2.photo_id = p2.id WHERE u.id != p2.user_id AND pt.tag_id = pt2.tag_id);")
                        st.subheader("Users with Unique Tags:")
                        
                        query = """
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

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_uwu) 

                    elif user_query_type == "User's Contribution to Tag Popularity":
                        query_result_ctt = run_query("SELECT u.id, u.username, t.tag_name, COUNT(pt.photo_id) AS tag_contribution FROM users u JOIN photos p ON u.id = p.user_id JOIN photo_tags pt ON p.id = pt.photo_id JOIN tags t ON pt.tag_id = t.id GROUP BY u.id, u.username, t.tag_name ORDER BY tag_contribution DESC;")
                        st.subheader("User's Contribution to Tag Popularity:")
                        
                        query = """
            SELECT u.id, u.username, t.tag_name, COUNT(pt.photo_id) AS tag_contribution
            FROM users u
            JOIN photos p ON u.id = p.user_id
            JOIN photo_tags pt ON p.id = pt.photo_id
            JOIN tags t ON pt.tag_id = t.id
            GROUP BY u.id, u.username, t.tag_name
            ORDER BY tag_contribution DESC;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_ctt) 

                    elif user_query_type == 'Users Who Follow Each Other':
                        query_result_fee = run_query("SELECT f1.follower_id AS follower_id, u1.username AS follower_name, f1.followee_id AS followee_id, u2.username AS followee_name FROM follows f1 JOIN follows f2 ON f1.follower_id = f2.followee_id AND f1.followee_id = f2.follower_id JOIN users u1 ON f1.follower_id = u1.id JOIN users u2 ON f1.followee_id = u2.id WHERE f1.follower_id < f1.followee_id;")
                        st.subheader("Users Who Follow Each Other:")
                        
                        query = """
            SELECT f1.follower_id AS follower_id, u1.username AS follower_name, f1.followee_id AS followee_id, u2.username AS followee_name
            FROM follows f1
            JOIN follows f2 ON f1.follower_id = f2.followee_id AND f1.followee_id = f2.follower_id
            JOIN users u1 ON f1.follower_id = u1.id
            JOIN users u2 ON f1.followee_id = u2.id
            WHERE f1.follower_id < f1.followee_id;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_fee)
                        
        elif selected_query_type == 'Photo Query':
            st.sidebar.subheader("Photo Queries")
            photo_query_type = st.sidebar.selectbox('Select a query type:', ['Photos with Rank and Like Counts', 'Photo with the Most Likes', 'Average Likes per Photo','Photos with No Likes','Photos Tagged with Multiple Tags','TOP 5 Photos with Highest Comments','Top 5 Photos with Most Engagement','Photos with Similar Tags'])

                     
            if photo_query_type:
                st.sidebar.checkbox("Show Query Info", key=f"photo_{photo_query_type}")
                run_photo_query = st.sidebar.button("Run Photo Query")

                if run_photo_query:
                    if photo_query_type == 'Photos with Rank and Like Counts':
                        query_result_likes = run_query("WITH ranked_photos AS (SELECT photo_id, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS photo_rank, COUNT(*) AS likes_count FROM likes GROUP BY photo_id) SELECT photo_id, photo_rank, likes_count FROM ranked_photos WHERE photo_rank <= 5;")
                        st.subheader("Photos with Rank and Like Counts:")
                        
                        query = """
            WITH ranked_photos AS (
                SELECT photo_id, DENSE_RANK() OVER (ORDER BY COUNT(*) DESC) AS photo_rank, COUNT(*) AS likes_count
                FROM likes
                GROUP BY photo_id
            )
            SELECT photo_id, photo_rank, likes_count
            FROM ranked_photos
            WHERE photo_rank <= 5;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_likes)
                        
                    elif photo_query_type == 'Photo with the Most Likes':
                        query_result_ftm = run_query("SELECT l.photo_id, p.image_url, COUNT(*) AS likes_count FROM likes l JOIN photos p ON l.photo_id = p.id GROUP BY l.photo_id, p.image_url HAVING likes_count = (SELECT MAX(likes_count) FROM (SELECT COUNT(*) AS likes_count FROM likes GROUP BY photo_id) AS max_likes);")
                        st.subheader("Photo with the Most Likes:")
                        
                        query = """
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

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_ftm)

                    elif photo_query_type == 'Average Likes per Photo':
                        query_result_alp = run_query("SELECT p.photo_id, ph.image_url, AVG(p.likes_count) AS avg_likes_per_photo FROM (SELECT l.photo_id, COUNT(*) AS likes_count FROM likes l GROUP BY l.photo_id) AS p JOIN photos ph ON p.photo_id = ph.id GROUP BY p.photo_id, ph.image_url;")
                        st.subheader("Average Likes per Photo:")
                        
                        query = """
            SELECT p.photo_id, ph.image_url, AVG(p.likes_count) AS avg_likes_per_photo
            FROM (
                SELECT l.photo_id, COUNT(*) AS likes_count
                FROM likes l
                GROUP BY l.photo_id
            ) AS p
            JOIN photos ph ON p.photo_id = ph.id
            GROUP BY p.photo_id, ph.image_url;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_alp)

                    elif photo_query_type == 'Photos with No Likes':
                        query_result_fwn = run_query("SELECT p.id, p.image_url FROM photos p LEFT JOIN likes l ON p.id = l.photo_id WHERE l.user_id IS NULL;")
                        st.subheader("Photos with No Likes:")
                        
                        query = """
            SELECT p.id, p.image_url
            FROM photos p
            LEFT JOIN likes l ON p.id = l.photo_id
            WHERE l.user_id IS NULL;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_fwn)  

                    elif photo_query_type == 'Photos Tagged with Multiple Tags':
                        query_result_fwm = run_query("SELECT p.id, p.image_url, COUNT(pt.tag_id) AS tags_count FROM photos p JOIN photo_tags pt ON p.id = pt.photo_id GROUP BY p.id HAVING tags_count > 4;")
                        st.subheader("Photos Tagged with Multiple Tags:")
                        
                        query = """
            SELECT p.id, p.image_url, COUNT(pt.tag_id) AS tags_count
            FROM photos p
            JOIN photo_tags pt ON p.id = pt.photo_id
            GROUP BY p.id
            HAVING tags_count > 4;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_fwm)   

                    elif photo_query_type == 'TOP 5 Photos with Highest Comments':
                        query_result_fmac = run_query("SELECT u.username, p.id AS photo_id, RANK() OVER (ORDER BY COUNT(c.id) DESC) AS photo_rank, COUNT(c.id) AS comments_count FROM photos p JOIN comments c ON p.id = c.photo_id JOIN users u ON p.user_id = u.id GROUP BY p.id, u.username LIMIT 5;")
                        st.subheader("TOP 5 Photos with Highest Comments:")
                        
                        query = """
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

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_fmac)    
   

                    elif photo_query_type == 'Top 5 Photos with Most Engagement':
                        query_result_pme = run_query("SELECT p.id, p.image_url, (COALESCE(l.total_likes, 0) + COALESCE(c.total_comments, 0)) AS total_engagement FROM photos p LEFT JOIN (SELECT photo_id, COUNT(*) AS total_likes FROM likes GROUP BY photo_id) l ON p.id = l.photo_id LEFT JOIN (SELECT photo_id, COUNT(*) AS total_comments FROM comments GROUP BY photo_id) c ON p.id = c.photo_id ORDER BY total_engagement DESC LIMIT 5;")
                        st.subheader("Top 5 Photos with Most Engagement(likes + comments):")
                        
                        query = """
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

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_pme)

                    elif photo_query_type == 'Photos with Similar Tags':
                        query_result_pst = run_query("SELECT DISTINCT p1.id, p1.image_url, p2.id AS similar_photo_id, p2.image_url AS The_image_url FROM photos p1 JOIN photo_tags pt1 ON p1.id = pt1.photo_id JOIN photos p2 ON p1.id < p2.id JOIN photo_tags pt2 ON p2.id = pt2.photo_id AND pt1.tag_id = pt2.tag_id GROUP BY p1.id, p1.image_url, similar_photo_id, The_image_url HAVING COUNT(DISTINCT pt1.tag_id) >= 3;")
                        st.subheader("Photos with Similar Tags:")
                        
                        query = """
            SELECT DISTINCT p1.id, p1.image_url, p2.id AS similar_photo_id, p2.image_url AS The_image_url
            FROM photos p1
            JOIN photo_tags pt1 ON p1.id = pt1.photo_id
            JOIN photos p2 ON p1.id < p2.id
            JOIN photo_tags pt2 ON p2.id = pt2.photo_id AND pt1.tag_id = pt2.tag_id
            GROUP BY p1.id, p1.image_url, similar_photo_id, The_image_url
            HAVING COUNT(DISTINCT pt1.tag_id) >= 3;

        """
                        st.code(query, language='sql')
                        st.subheader("Query Result:")
                        st.dataframe(query_result_pst)

# Main Streamlit app
def main():
    interactive_query()
    display_introduction()
    st.markdown(
        """<div style="position: fixed; bottom: 0; right: 0; padding: 10px;">
           Created with ❤️ by Darshan Panchal
           </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()