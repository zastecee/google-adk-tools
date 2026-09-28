-- =============================================
-- Author:      Almeida de Almeida
-- Create date: 03/09/2026
-- Description: API for getting the customer segment for the GoRhino.
--
-- Change History:
--   03/09/2026 Almeida de Almeida: Initial Commit.
-- =============================================

DECLARE
    l_requestid     VARCHAR2(100);
    l_msisdn        VARCHAR2(20);
    l_body          CLOB;
    l_status_code   NUMBER;
    l_response_code NUMBER;
    l_status        VARCHAR2(40);
    l_action        VARCHAR2(40);
    l_message       VARCHAR2(400);
    l_level         NUMBER;
    l_timestamp     TIMESTAMP;
    v_segment       VARCHAR2(20);
    v_msisdn        VARCHAR2(20);  

BEGIN
    v_msisdn := :msisdn;


    owa_util.mime_header('application/json', FALSE);
    htp.p('Cache-Control: no-cache');
    owa_util.http_header_close;


    -- Validate MSISDN
    IF v_msisdn IS NULL 
        OR TRIM(v_msisdn) IS NULL 
        OR LENGTH(v_msisdn) < 12  
        OR (
          SUBSTR(v_msisdn, 1, 5) <> '25884'
          AND SUBSTR(v_msisdn, 1, 5) <> '25885'
        )
        THEN

        l_status_code := 400;
        owa_util.status_line(l_status_code, 'Bad Request');
        owa_util.http_header_close;

        htp.p(JSON_OBJECT(
                'responseStatus' VALUE 'ERROR',
                'responseMessage' VALUE 'Invalid msisdn'
              ));
        RETURN;
    END IF;

    --- Query Data
    SELECT NVL(GRS_SEGMENT,'NOT_FOUND') INTO v_segment FROM svc_da_rep.AGG_GRS_GORHINO_CUSTOMER_SEGMENT
    WHERE grs_msisdn = v_msisdn;

    IF v_segment = 'NOT_FOUND' THEN
      l_status_code := 404;
      owa_util.status_line(l_status_code, 'Bad Request');
      owa_util.http_header_close;

      htp.p(JSON_OBJECT(
              'responseStatus' VALUE 'ERROR',
              'responseMessage' VALUE 'msisdn not found.'
            ));
      RETURN;
    END IF;

    htp.p(
            JSON_OBJECT(
                    'segments' VALUE v_segment
            )
    );

EXCEPTION
    WHEN NO_DATA_FOUND THEN
        l_status_code := 404;
        htp.p(JSON_OBJECT(
            'responseStatus' VALUE 'ERROR',
            'responseMessage' VALUE 'msisdn not found.'
        ));

    WHEN OTHERS THEN
        l_status_code := 500;
        owa_util.status_line(l_status_code, 'Bad Request');
        owa_util.http_header_close;

        htp.p(JSON_OBJECT(
                'responseStatus' VALUE 'ERROR',
                'responseMessage' VALUE 'Server Fault.'
              ));
END;













-- 

SELECT NVL(GRS_SEGMENT,'NOT_FOUND') INTO v_segment FROM svc_da_rep.AGG_GRS_GORHINO_CUSTOMER_SEGMENT
    WHERE grs_msisdn = v_msisdn;

select JSON_ARRAYAGG(JSON_OBJECT(*)) into VARCHAR2_variable from svc_da_rep.AGG_GRS_GORHINO_CUSTOMER_SEGMENT
where GRS_MSISDN in ('258840188953', '258858497371', '258858537703')
;

select JSON_OBJECT(
            'transactions' VALUE (
                select JSON_ARRAYAGG(JSON_OBJECT(*)) from svc_da_rep.AGG_GRS_GORHINO_CUSTOMER_SEGMENT
                where GRS_MSISDN in ('258840188953', '258858497371', '258858537703')
            ),
            'service_type' VALUE 'DATA'
        )
FROM dual
;

DECLARE
    transactions VARCHAR2 (4000);
    subscriber VARCHAR2(255);
BEGIN
    select JSON_ARRAYAGG(JSON_OBJECT(*)) into transactions from svc_da_rep.AGG_GRS_GORHINO_CUSTOMER_SEGMENT
                where GRS_MSISDN in ('258840188953', '258858497371', '258858537703');

    --DBMS_OUTPUT.PUT_LINE (transactions);

    select JSON_OBJECT('msisdn' VALUE '258840188953') into subscriber from dual;
    -- DBMS_OUTPUT.PUT_LINE (subscriber);

    DBMS_OUTPUT.PUT_LINE(JSON_OBJECT('subscriber' VALUE subscriber, 'transactions' VALUE transactions));
    
END;
/