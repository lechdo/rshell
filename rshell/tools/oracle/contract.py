
SELECT_TABLE_COLUMNS_BY_TABLE_NAME_AND_OWNER = """
SELECT COLUMN_NAME FROM (
    SELECT UNIQUE atc.COLUMN_ID, atc.COLUMN_NAME from ALL_TAB_COLUMNS atc
        JOIN ALL_SYNONYMS als ON atc.OWNER = als.TABLE_OWNER
        WHERE atc.TABLE_NAME = :table_name
        AND als.OWNER = :owner
        ORDER BY atc.COLUMN_ID
    )"""