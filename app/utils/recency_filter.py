from datetime import datetime,timedelta

def build_recency_filter(search_period):

    now = datetime.utcnow()

    if search_period=="LAST_WEEK":
        return {
            "$gte": now-timedelta(days=7)
        }

    if search_period=="LAST_MONTH":
        return {
            "$gte": now-timedelta(days=30)
        }

    return {
        "$gte": datetime(2000,1,1)
    }