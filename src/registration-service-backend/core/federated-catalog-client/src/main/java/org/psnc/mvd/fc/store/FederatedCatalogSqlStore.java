
package org.psnc.mvd.fc.store;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.eclipse.edc.spi.persistence.EdcPersistenceException;
import org.eclipse.edc.sql.QueryExecutor;
import org.eclipse.edc.sql.store.AbstractSqlStore;
import org.eclipse.edc.transaction.datasource.spi.DataSourceRegistry;
import org.eclipse.edc.transaction.spi.TransactionContext;
import org.psnc.mvd.fc.store.statements.DatasetCatalogSqlStatements;
import org.psnc.mvd.fc.store.statements.TargetNodeDirectorySqlStatements;

import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;

public class FederatedCatalogSqlStore extends AbstractSqlStore {

    private DatasetCatalogSqlStatements datasetStatements;
    private TargetNodeDirectorySqlStatements targetNodeStatements;

    public FederatedCatalogSqlStore(DataSourceRegistry dataSourceRegistry, String dataSourceName, TransactionContext transactionContext,
                                  ObjectMapper objectMapper, QueryExecutor queryExecutor,
                                  DatasetCatalogSqlStatements datasetStatements, TargetNodeDirectorySqlStatements targetNodeStatements) {
        super(dataSourceRegistry, dataSourceName, transactionContext, objectMapper, queryExecutor);
        this.datasetStatements = datasetStatements;
        this.targetNodeStatements = targetNodeStatements;
    }

    public void deleteParticipant(String did) {
        transactionContext.execute(() -> {
            try (var connection = getConnection()) {
                var targetNodeProtocolUrl = getTargetNodeProtocolUrl(connection, did);
                var datasetDeleteStatement = datasetStatements.getDeleteDatasetCatalogCacheTemplate();
                queryExecutor.execute(connection,
                    datasetDeleteStatement,
                    targetNodeProtocolUrl
                );
                var targetNodeDeleteStatement = targetNodeStatements.getDeleteTargetNodeTemplate();
                queryExecutor.execute(connection,
                    targetNodeDeleteStatement,
                    did
                );
            } catch (SQLException e) {
                throw new EdcPersistenceException(e);
            }
        });
    }

    public void insertParticipant(String did, String protocolUrl) {
        transactionContext.execute(() -> {
            try (var connection = getConnection()) {
                var insertTargetNode = targetNodeStatements.getInsertTargetNodeTemplate();
                queryExecutor.execute(connection,
                        insertTargetNode,
                        did,
                        did,
                        protocolUrl,
                        "[\"dataspace-protocol-http\"]"
                );
            } catch (SQLException e) {
                throw new EdcPersistenceException(e);
            }
        });
    }

    private String getTargetNodeProtocolUrl(Connection connection, String did) {
        try (var stream = queryExecutor.query(connection, false, this::targetUrlMapper, targetNodeStatements.getSelectTargetNodeProtocolUrl(), did)) {
            return stream.findFirst().orElse(null);
        }
    }

    private String targetUrlMapper(ResultSet resultSet) throws SQLException {
        return resultSet.getString(targetNodeStatements.getTargetUrlColumn());
    }
}
