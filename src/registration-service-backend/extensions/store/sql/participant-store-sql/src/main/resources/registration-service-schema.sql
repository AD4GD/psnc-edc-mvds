CREATE TABLE IF NOT EXISTS edc_participant
(
    id                   VARCHAR NOT NULL PRIMARY KEY,
    did                  VARCHAR NOT NULL UNIQUE,
    protocol_url          VARCHAR NOT NULL UNIQUE,
    state                INTEGER DEFAULT 0 NOT NULL,
    state_count          INTEGER DEFAULT 0 NOT NULL,
    state_timestamp      BIGINT,
    error_detail         VARCHAR,
    trace_context        JSON,
    created_at           BIGINT NOT NULL,
    updated_at           BIGINT NOT NULL
);

-- fc tables
CREATE TABLE IF NOT EXISTS edc_target_node_directory
(
    id                      VARCHAR PRIMARY KEY NOT NULL,
    name                    VARCHAR NOT NULL,
    target_url              VARCHAR NOT NULL,
    supported_protocols     JSON
);

COMMENT ON COLUMN edc_target_node_directory.supported_protocols IS 'List<String> serialized as JSON';

CREATE TABLE IF NOT EXISTS edc_federated_catalog
(
    id                    VARCHAR PRIMARY KEY NOT NULL,
    catalog               JSON,
    marked                BOOLEAN DEFAULT FALSE
);
