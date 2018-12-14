import click
from google.cloud import bigquery

uni1 = 'jq2282' # Your uni
uni2 = 'zw2498' # Partner's uni. If you don't have a partner, put None

# Test function
def testquery(client):
    q = """select * from `w4111-columbia.graph.tweets` limit 3"""
    job = client.query(q)

    # waits for query to execute and return
    results = job.result()
    # results = list(results)
    # output = open('data3.xls', 'w')
    # output.write('idx\create_time\id\in_reply\like_num\quoted_org_id\retweet_num\retweet_org_id\text\twitter_username\twitch_username\n')

    # for i in range(3):
    #     for j in results[i]:
    #         output.write(str(j))
    #         output.write('\t')
    #     output.write('\n')
    # output.close()
    # return results
    return list(results)

# SQL query for Question 1. You must edit this funtion.
# This function should return a list of IDs and the corresponding text.
def q1(client):
    var1 = 'going live'
    var2 = 'https://www.twitch' #there is no twitch.com now, only twitch.tv
    #var2 = 'https://t.co/'
    q = """select id, text from `w4111-columbia.graph.tweets` where text like '%%%s%%' and text like '%%%s%%'""" %(var1, var2) 
    job = client.query(q)
    results = job.result()
    #print(results)
    return list(results)

# SQL query for Question 2. You must edit this funtion.
# This function should return a list of days and their corresponding average likes.
def q2(client):
    q = """select substr(create_time, 1, 3) as day, avg(like_num) as alike from `w4111-columbia.graph.tweets` group by day order by alike desc limit 7"""
    #if no limit, may have none values
    job = client.query(q)
    results = job.result()
    #print(results)
    return list(results)
    #return []

# SQL query for Question 3. You must edit this funtion.
# This function should return a list of source nodes and destination nodes in the graph.
def q3(client):
    q = '''
CREATE OR REPLACE TABLE
  dataset.GRAPH AS (
  SELECT
    DISTINCT twitter_username AS src,
    SUBSTR(REGEXP_EXTRACT(text, r"\s([@][\w_-]+)"),2) AS dst
  FROM
    `w4111-columbia.graph.tweets`
  WHERE
    REGEXP_EXTRACT(text, r"\s([@][\w_-]+)") IS NOT NULL
    AND twitter_username != SUBSTR(REGEXP_EXTRACT(text, r"\s([@][\w_-]+)"),2))
        '''
    job = client.query(q)
    results = job.result()
    return [] 

# SQL query for Question 4. You must edit this funtion.
# This function should return a list containing the twitter username of the users having the max indegree and max outdegree.
def q4(client):
    q = '''
        select tmp1.src AS max_indegree, tmp2.dst AS max_outdegree
        from (
            select dst from dataset.GRAPH group by dst order by count(*) desc limit 1) as tmp1,
            (
            select src from dataset.GRAPH group by src order by count(*) desc limit 1) as tmp2

    '''
    job = client.query(q)
    results = job.result()
    return list(results)

# SQL query for Question 5. You must edit this funtion.
# This function should return a list containing value of the conditional probability.
def q5(client):
    q = '''
create or replace view dataset.unpop as (
  select twitter_username from (
    select avg(W.like_num) as usr_like, twitter_username from `w4111-columbia.graph.tweets` W
    group by W.twitter_username
  ) as temp
  where temp.usr_like < (
    select avg(usr_like) from (
      select avg(W.like_num) as usr_like, twitter_username from `w4111-columbia.graph.tweets` W
    group by W.twitter_username
    ) as tmp
  )
  intersect distinct
  select dst from (
    select dst, count(*) as indegree from `proj2graph.dataset.GRAPH` group by dst
  ) as tmp1
  where tmp1.indegree < (
    select avg(indegree) from (
      select dst, count(*) as indegree from `proj2graph.dataset.GRAPH` group by dst
    ) as tmp2
  )
)
'''
    job = client.query(q)
    results = job.result()
    q = '''
create or replace view dataset.pop as (
  select twitter_username from (
    select avg(W.like_num) as usr_like, twitter_username from `w4111-columbia.graph.tweets` W
    group by W.twitter_username
  ) as temp
  where temp.usr_like >= (
    select avg(usr_like) from (
      select avg(W.like_num) as usr_like, twitter_username from `w4111-columbia.graph.tweets` W
    group by W.twitter_username
    ) as tmp
  )
  intersect distinct
  select dst from (
    select dst, count(*) as indegree from `proj2graph.dataset.GRAPH` group by dst
  ) as tmp1
  where tmp1.indegree >= (
    select avg(indegree) from (
      select dst, count(*) as indegree from `proj2graph.dataset.GRAPH` group by dst
    ) as tmp2
  )
)

'''
    job = client.query(q)
    results = job.result()
    q = '''
select tmp1.mention/tmp2.ppl as popular_unpopular
from (
select distinct count(*) as mention from dataset.pop P, dataset.unpop U, dataset.GRAPH G
where U.twitter_username = G.src
and P.twitter_username = G.dst
) as tmp1,
(
select count(*) as ppl from dataset.unpop
) as tmp2
'''
    job = client.query(q)
    results = job.result()
    return list(results)

# SQL query for Question 6. You must edit this funtion.
# This function should return a list containing the value for the number of triangles in the graph.
def q6(client):
    q = '''
SELECT
  COUNT(*)
FROM
  dataset.GRAPH g1,
  dataset.GRAPH g2,
  dataset.GRAPH g3
WHERE
  g1.dst = g2.src
  AND g2.dst=g3.src
  AND g3.dst=g1.src
  AND g2.src<g3.src
  AND g1.src>g2.src
'''
    job = client.query(q)
    results = job.result()    
    return list(results)

# SQL query for Question 7. You must edit this funtion.
# This function should return a list containing the twitter username and their corresponding PageRank.
def q7(client):

    return []


# Do not edit this function. This is for helping you develop your own iterative PageRank algorithm.
def bfs(client, start, n_iter):

    # You should replace dataset.bfs_graph with your dataset name and table name.
    q1 = """
        CREATE TABLE IF NOT EXISTS dataset.bfs_graph (src string, dst string);
        """
    q2 = """
        INSERT INTO dataset.bfs_graph(src, dst) VALUES
        ('A', 'B'),
        ('A', 'E'),
        ('B', 'C'),
        ('C', 'D'),
        ('E', 'F'),
        ('F', 'D'),
        ('A', 'F'),
        ('B', 'E'),
        ('B', 'F'),
        ('A', 'G'),
        ('B', 'G'),
        ('F', 'G'),
        ('H', 'A'),
        ('G', 'H'),
        ('H', 'C'),
        ('H', 'D'),
        ('E', 'H'),
        ('F', 'H');
        """

    job = client.query(q1)
    results = job.result()
    job = client.query(q2)
    results = job.result()

    # You should replace dataset.distances with your dataset name and table name. 
    q3 = """
        CREATE OR REPLACE TABLE dataset.distances AS
        SELECT '{start}' as node, 0 as distance
        """.format(start=start)
    job = client.query(q3)
    # Result will be empty, but calling makes the code wait for the query to complete
    job.result()

    for i in range(n_iter):
        print("Step %d..." % (i+1))
        q1 = """
        INSERT INTO dataset.distances(node, distance)
        SELECT distinct dst, {next_distance}
        FROM dataset.bfs_graph
            WHERE src IN (
                SELECT node
                FROM dataset.distances
                WHERE distance = {curr_distance}
                )
            AND dst NOT IN (
                SELECT node
                FROM dataset.distances
                )
            """.format(
                curr_distance=i,
                next_distance=i+1
            )
        job = client.query(q1)
        results = job.result()
        # print(results)


# Do not edit this function. You can use this function to see how to store tables using BigQuery.
def save_table(name, sql):
    client = bigquery.Client()
    dataset_id = 'graph'

    job_config = bigquery.QueryJobConfig()
    # Set use_legacy_sql to True to use legacy SQL syntax.
    job_config.use_legacy_sql = True
    # Set the destination table
    table_ref = client.dataset(dataset_id).table(name)
    job_config.destination = table_ref
    job_config.allow_large_results = True

    # Start the query, passing in the extra configuration.
    query_job = client.query(
        sql,
        # Location must match that of the dataset(s) referenced in the query
        # and of the destination table.
        location='US',
        job_config=job_config)  # API request - starts the query

    return query_job.result()  # Waits for the query to finish
    

@click.command()
@click.argument("PATHTOCRED", type=click.Path(exists=True))
def main(pathtocred):
    client = bigquery.Client.from_service_account_json(pathtocred)

    #funcs_to_test = [q1, q2, q3, q4, q5, q6, q7]
    funcs_to_test = [q5]
    for func in funcs_to_test:
        rows = func(client)
        print ("\n====%s====" % func.__name__)
        print(rows)

    #bfs(client, 'A', 5)

if __name__ == "__main__":
  main()
