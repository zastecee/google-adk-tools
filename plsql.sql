-- DECLARE
--     V_YEAR NUMBER;
-- BEGIN   
--     V_YEAR := 2026;

--     DBMS_OUTPUT.PUT_LINE('Year: ' || V_YEAR);
-- END;
-- /

-- DECLARE
--     V_YEAR NUMBER;
-- BEGIN
--     V_YEAR := EXTRACT(YEAR FROM SYSDATE);

--     DBMS_OUTPUT.PUT_LINE('Year: ' || V_YEAR);
-- END;
-- /

-- CREATE OR REPLACE PROCEDURE HELLO_WORLD_245 (V_YEAR NUMBER) 
-- AS 
-- BEGIN
--     DBMS_OUTPUT.PUT_LINE('Year: ' || V_YEAR);
-- END;
-- /

-- EXEC HELLO_WORLD_245(245)



CREATE OR REPLACE PROCEDURE LOAD_CCS_DATA_USAGE_245
AS
BEGIN

    -----------------------------------------------------------------
    -- Limpa últimos 1 dias no destino
    -----------------------------------------------------------------
    DELETE FROM SVC_ORDS_BDATA.CCS_DATA_USAGE@ORDS_DBLINK
    WHERE EVENT_START >= TRUNC(SYSDATE) - 1;

    -----------------------------------------------------------------
    -- Recarrega últimos 1 dias
    -----------------------------------------------------------------
    INSERT INTO SVC_ORDS_BDATA.CCS_DATA_USAGE@ORDS_DBLINK
    (
        EVENT_START,
        EVENT_END,
        EVENT_TYPE,
        TARIFF_PLAN,
        MSISDN,
        MTC_RECEPTOR,
        DURATION,
        INITIAL_VALUE_MB,
        CHARGED_VALUE_MB,
        REMAINING_VALUE_MB,
        OFFER_NAME,
        EXPIRY_DATE,
        ROAMING_COUNTRY
    )
    SELECT DISTINCT
           CC_RECORD_OPENING_TIME                                  AS EVENT_START,
           CC_RECORD_CLOSING_TIME                                  AS EVENT_END,
           CC_RECORD_TYPE                                          AS EVENT_TYPE,
           CC_PROVIDER_ID                                          AS TARIFF_PLAN,
           CC_MSISDN                                               AS MSISDN,
           CC_OTHER_PARTY_ADDRESS                                  AS MTC_RECEPTOR,
           CC_CC_TIME                                              AS DURATION,
           ROUND(CC_BALANCE_BEFORE / 1024 / 1024, 2)              AS INITIAL_VALUE_MB,
           ROUND(CC_CC_TOTAL_OCTETS / 1024 / 1024, 2)            AS CHARGED_VALUE_MB,
           ROUND(CC_COUNTER_FINAL_VALUE / 1024 / 1024, 2)        AS REMAINING_VALUE_MB,
           CC_OFFER_NAME                                           AS OFFER_NAME,
           CC_EXPIRY_DATE                                          AS EXPIRY_DATE,
           CC_ROAMING_COUNTRY                                      AS ROAMING_COUNTRY
    FROM ODS.STG_CC_CCS_CDR
    WHERE CC_RECORD_OPENING_TIME >= TRUNC(SYSDATE) - 1;

    COMMIT;

EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        RAISE;
END LOAD_CCS_DATA_USAGE_245;
/



----

from datetime import timedelta

import pendulum
from airflow.providers.oracle.hooks.oracle import OracleHook
from airflow.sdk import dag, task


@dag(
    dag_id="DATA_STATEMENT",
    schedule="0 * * * *",  # hora a hora
    start_date=pendulum.datetime(2026, 1, 1, tz="Africa/Maputo"),
    catchup=False,
    max_active_runs=1,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
)
def ccs_data_usage_load():

    @task
    def load_data_usage():

        conn = OracleHook(oracle_conn_id="ORDS_245").get_conn()

        try:
            with conn.cursor() as cur:
                cur.execute("""
                    BEGIN
                        LOAD_CCS_DATA_USAGE_245;
                    END;
                """)
            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            conn.close()

    load_data_usage()


ccs_data_usage_load()
