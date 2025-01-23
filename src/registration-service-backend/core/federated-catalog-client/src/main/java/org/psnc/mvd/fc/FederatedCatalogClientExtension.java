
package org.psnc.mvd.fc;

import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Provider;
import org.eclipse.edc.runtime.metamodel.annotation.Setting;
import org.eclipse.edc.spi.EdcException;
import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.spi.types.TypeManager;
import org.eclipse.edc.sql.QueryExecutor;
import org.eclipse.edc.transaction.datasource.spi.DataSourceRegistry;
import org.eclipse.edc.transaction.spi.TransactionContext;
import org.psnc.mvd.fc.store.FederatedCatalogSqlStore;
import org.psnc.mvd.fc.store.statements.DatasetCatalogSqlStatements;
import org.psnc.mvd.fc.store.statements.TargetNodeDirectorySqlStatements;

import static java.lang.String.format;

@Extension(FederatedCatalogClientExtension.NAME)
public class FederatedCatalogClientExtension implements ServiceExtension {

    public static final String NAME = "Federated Catalog Client Service";

    @Setting
    private static final String FEDERATED_CATALOG_DATASOURCE_NAME_SETTING = "psnc.federatedcatalog.datasource";

    @Inject
    private Monitor monitor;

    @Inject
    private DataSourceRegistry dataSourceRegistry;
    @Inject
    private TransactionContext trxContext;
    @Inject
    private TypeManager typeManager;
    @Inject
    private QueryExecutor queryExecutor;

    @Override
    public String name() {
        return NAME;
    }

    @Provider
    public FederatedCatalogClient federatedCatalogClient(ServiceExtensionContext context) {
        var datasource = context.getSetting(FEDERATED_CATALOG_DATASOURCE_NAME_SETTING, "default");

        var store = new FederatedCatalogSqlStore(
            dataSourceRegistry,
            datasource,
            trxContext,
            typeManager.getMapper(),
            queryExecutor,
            GetDatasetCatalogSqlStatements(),
            GetTargetNodeDirectorySqlStatements());

        return new FederatedCatalogClientImpl(monitor, store);
    }

    private DatasetCatalogSqlStatements GetDatasetCatalogSqlStatements() {
        return new DatasetCatalogSqlStatements();
    }

    private TargetNodeDirectorySqlStatements GetTargetNodeDirectorySqlStatements() {
        return new TargetNodeDirectorySqlStatements();
    }
}
