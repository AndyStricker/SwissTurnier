CONNECT_INFO='-h localhost -p 5432 -U stuser'
DBNAME='swissturnier'
pg_dump $CONNECT_INFO --schema=public --schema-only -f swissturnier.sql $DBNAME
pg_dump $CONNECT_INFO --schema=public --data-only -f category.sql --table=category $DBNAME
pg_dump $CONNECT_INFO --schema=public --data-only -f team.sql --table=team $DBNAME
pg_dump $CONNECT_INFO --schema=public --data-only -f playround.sql --table=playround $DBNAME
pg_dump $CONNECT_INFO --schema=public --data-only -f rankings.sql --table=rankings $DBNAME
