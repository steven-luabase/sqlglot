from tests.dialects.test_dialect import Validator


class TestRedshift(Validator):
    dialect = "redshift"

    def test_redshift(self):
        self.validate_all("CONVERT(INTEGER, x)", write={"redshift": "CAST(x AS INTEGER)"})
        self.validate_all(
            "DATE_ADD('day', ndays, caldate)", write={"redshift": "DATEADD('day', ndays, caldate)"}
        )
        self.validate_all(
            'create table "group" ("col" char(10))',
            write={
                "redshift": 'CREATE TABLE "group" ("col" CHAR(10))',
                "mysql": "CREATE TABLE `group` (`col` CHAR(10))",
            },
        )
        self.validate_all(
            'create table if not exists city_slash_id("city/id" integer not null, state char(2) not null)',
            write={
                "redshift": 'CREATE TABLE IF NOT EXISTS city_slash_id ("city/id" INTEGER NOT NULL, state CHAR(2) NOT NULL)',
                "presto": 'CREATE TABLE IF NOT EXISTS city_slash_id ("city/id" INTEGER NOT NULL, state CHAR(2) NOT NULL)',
            },
        )
        self.validate_all(
            "SELECT ST_AsEWKT(ST_GeomFromEWKT('SRID=4326;POINT(10 20)')::geography)",
            write={
                "redshift": "SELECT ST_ASEWKT(CAST(ST_GEOMFROMEWKT('SRID=4326;POINT(10 20)') AS GEOGRAPHY))",
                "bigquery": "SELECT ST_ASEWKT(CAST(ST_GEOMFROMEWKT('SRID=4326;POINT(10 20)') AS GEOGRAPHY))",
            },
        )
        self.validate_all(
            "SELECT ST_AsEWKT(ST_GeogFromText('LINESTRING(110 40, 2 3, -10 80, -7 9)')::geometry)",
            write={
                "redshift": "SELECT ST_ASEWKT(CAST(ST_GEOGFROMTEXT('LINESTRING(110 40, 2 3, -10 80, -7 9)') AS GEOMETRY))",
            },
        )
        self.validate_all(
            "SELECT 'abc'::BINARY",
            write={
                "redshift": "SELECT CAST('abc' AS VARBYTE)",
            },
        )
        self.validate_all(
            "SELECT 'abc'::CHARACTER",
            write={
                "redshift": "SELECT CAST('abc' AS CHAR)",
            },
        )
        self.validate_all(
            "SELECT * FROM venue WHERE (venuecity, venuestate) IN (('Miami', 'FL'), ('Tampa', 'FL')) ORDER BY venueid",
            write={
                "redshift": "SELECT * FROM venue WHERE (venuecity, venuestate) IN (('Miami', 'FL'), ('Tampa', 'FL')) ORDER BY venueid",
            },
        )
        self.validate_all(
            'SELECT tablename, "column" FROM pg_table_def WHERE "column" LIKE \'%start\\_%\' LIMIT 5',
            write={
                "redshift": 'SELECT tablename, "column" FROM pg_table_def WHERE "column" LIKE \'%start\\_%\' LIMIT 5'
            },
        )
        self.validate_all(
            "SELECT DISTINCT ON (a) a, b FROM x ORDER BY c DESC",
            write={
                "redshift": 'SELECT a, b FROM (SELECT a, b, ROW_NUMBER() OVER (PARTITION BY a ORDER BY c DESC) AS _row_number FROM x) WHERE "_row_number" = 1',
            },
        )
        self.validate_all(
            "DECODE(x, a, b, c, d)",
            write={
                "": "MATCHES(x, a, b, c, d)",
                "oracle": "DECODE(x, a, b, c, d)",
                "snowflake": "DECODE(x, a, b, c, d)",
            },
        )
        self.validate_all(
            "NVL(a, b, c, d)",
            write={
                "redshift": "COALESCE(a, b, c, d)",
                "mysql": "COALESCE(a, b, c, d)",
                "postgres": "COALESCE(a, b, c, d)",
            },
        )
        self.validate_all(
            "DATEDIFF(d, a, b)",
            write={
                "redshift": "DATEDIFF(d, a, b)",
                "presto": "DATE_DIFF(d, a, b)",
            },
        )
        self.validate_all(
            "SELECT TOP 1 x FROM y",
            write={
                "redshift": "SELECT x FROM y LIMIT 1",
            },
        )

    def test_identity(self):
        self.validate_identity(
            "SELECT DECODE(COL1, 'replace_this', 'with_this', 'replace_that', 'with_that')"
        )
        self.validate_identity("CAST('bla' AS SUPER)")
        self.validate_identity("CREATE TABLE real1 (realcol REAL)")
        self.validate_identity("CAST('foo' AS HLLSKETCH)")
        self.validate_identity("SELECT DATEADD(day, 1, 'today')")
        self.validate_identity("'abc' SIMILAR TO '(b|c)%'")
        self.validate_identity(
            "SELECT caldate + INTERVAL '1 second' AS dateplus FROM date WHERE caldate = '12-31-2008'"
        )
        self.validate_identity("CREATE TABLE datetable (start_date DATE, end_date DATE)")
        self.validate_identity(
            "SELECT COUNT(*) FROM event WHERE eventname LIKE '%Ring%' OR eventname LIKE '%Die%'"
        )
        self.validate_identity(
            "CREATE TABLE SOUP (LIKE other_table) DISTKEY(soup1) SORTKEY(soup2) DISTSTYLE ALL"
        )
        self.validate_identity(
            "CREATE TABLE sales (salesid INTEGER NOT NULL) DISTKEY(listid) COMPOUND SORTKEY(listid, sellerid) DISTSTYLE AUTO"
        )
        self.validate_identity(
            "COPY customer FROM 's3://mybucket/customer' IAM_ROLE 'arn:aws:iam::0123456789012:role/MyRedshiftRole'"
        )
        self.validate_identity(
            "UNLOAD ('select * from venue') TO 's3://mybucket/unload/' IAM_ROLE 'arn:aws:iam::0123456789012:role/MyRedshiftRole'"
        )
        self.validate_identity(
            "CREATE TABLE SOUP (SOUP1 VARCHAR(50) NOT NULL ENCODE ZSTD, SOUP2 VARCHAR(70) NULL ENCODE DELTA)"
        )

    def test_values(self):
        self.validate_all(
            "SELECT a, b FROM (VALUES (1, 2)) AS t (a, b)",
            write={
                "redshift": "SELECT a, b FROM (SELECT 1 AS a, 2 AS b) AS t",
            },
        )
        self.validate_all(
            "SELECT a, b FROM (VALUES (1, 2), (3, 4)) AS t (a, b)",
            write={
                "redshift": "SELECT a, b FROM (SELECT 1 AS a, 2 AS b UNION ALL SELECT 3, 4) AS t",
            },
        )
        self.validate_all(
            "SELECT a, b FROM (VALUES (1, 2), (3, 4), (5, 6), (7, 8)) AS t (a, b)",
            write={
                "redshift": "SELECT a, b FROM (SELECT 1 AS a, 2 AS b UNION ALL SELECT 3, 4 UNION ALL SELECT 5, 6 UNION ALL SELECT 7, 8) AS t",
            },
        )
        self.validate_all(
            "INSERT INTO t(a) VALUES (1), (2), (3)",
            write={
                "redshift": "INSERT INTO t (a) VALUES (1), (2), (3)",
            },
        )
        self.validate_all(
            "INSERT INTO t(a, b) SELECT a, b FROM (VALUES (1, 2), (3, 4)) AS t (a, b)",
            write={
                "redshift": "INSERT INTO t (a, b) SELECT a, b FROM (SELECT 1 AS a, 2 AS b UNION ALL SELECT 3, 4) AS t",
            },
        )
        self.validate_all(
            "INSERT INTO t(a, b) VALUES (1, 2), (3, 4)",
            write={
                "redshift": "INSERT INTO t (a, b) VALUES (1, 2), (3, 4)",
            },
        )

    def test_create_table_like(self):
        self.validate_all(
            "CREATE TABLE t1 LIKE t2",
            write={
                "redshift": "CREATE TABLE t1 (LIKE t2)",
            },
        )
        self.validate_all(
            "CREATE TABLE SOUP (LIKE other_table) DISTKEY(soup1) SORTKEY(soup2) DISTSTYLE ALL",
            write={
                "redshift": "CREATE TABLE SOUP (LIKE other_table) DISTKEY(soup1) SORTKEY(soup2) DISTSTYLE ALL",
            },
        )

    def test_rename_table(self):
        self.validate_all(
            "ALTER TABLE db.t1 RENAME TO db.t2",
            write={
                "spark": "ALTER TABLE db.t1 RENAME TO db.t2",
                "redshift": "ALTER TABLE db.t1 RENAME TO t2",
            },
        )

    def test_varchar_max(self):
        self.validate_all(
            "CREATE TABLE TEST (cola VARCHAR(MAX))",
            write={
                "redshift": 'CREATE TABLE "TEST" ("cola" VARCHAR(MAX))',
            },
            identify=True,
        )

    def test_no_schema_binding(self):
        self.validate_all(
            "CREATE OR REPLACE VIEW v1 AS SELECT cola, colb FROM t1 WITH NO SCHEMA BINDING",
            write={
                "redshift": "CREATE OR REPLACE VIEW v1 AS SELECT cola, colb FROM t1 WITH NO SCHEMA BINDING",
            },
        )
