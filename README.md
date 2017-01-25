# NTSB_bot
Uploads the latest NTSB aviation data to the chosen subreddit(Uses Reddit.com)

# File Descriptions
* AviationData.txt = the file downloaded from the NTSB.
* id_database.txt = stores the incident ids so the program knows what it's already uploaded.
* login.txt = stores the login info for the bot.
* post_id_database.txt = same as id_database.txt, but stores the reddit id instead of the NTSB id.
* NTSB_bot.py = the program.

# Example Output
```
Logging in as: RedditUser27
    Login Succesful
    
list index out of range
Invalid data!
Scan complete: Added 0 incidents!
```
or
```
Logging in as: RedditUser27
    Login Succesful
    
20170116X24104
C:\Python27\lib\site-packages\requests\packages\urllib3\connectionpool.py:843: InsecureRequestW
arning: Unverified HTTPS request is being made. Adding certificate verification is strongly adv
ised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
InsecureRequestWarning)
Appending
    Submitting post
        Post Submitted succesfully
        
20170136X24104
C:\Python27\lib\site-packages\requests\packages\urllib3\connectionpool.py:843: InsecureRequestW
arning: Unverified HTTPS request is being made. Adding certificate verification is strongly adv
ised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
InsecureRequestWarning)
Appending
    Submitting post
        Post Submitted succesfully
        
list index out of range
Invalid data!
Scan complete: Added 2 incidents!

```
