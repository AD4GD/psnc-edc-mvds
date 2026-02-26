package psnc;

import org.eclipse.edc.catalog.cache.sql.FederatedCatalogCacheStatements;
import org.eclipse.edc.runtime.metamodel.annotation.Extension;
import org.eclipse.edc.runtime.metamodel.annotation.Inject;
import org.eclipse.edc.runtime.metamodel.annotation.Provider;
import org.eclipse.edc.spi.query.Criterion;
import org.eclipse.edc.spi.system.ServiceExtension;
import org.eclipse.edc.spi.system.ServiceExtensionContext;
import org.eclipse.edc.sql.translation.CriterionToWhereClauseConverter;
import org.eclipse.edc.sql.translation.WhereClause;

@Extension(value = GeoSpatialFilteringExtension.NAME)
public class GeoSpatialFilteringExtension implements ServiceExtension {

    public static final String NAME = "Geo-spatial filtering";

    /**
     * Provider that registers a decorated converter.
     * We keep it as a Provider so EDC can manage construction order and injection.
     */
    @Provider
    public FederatedCatalogCacheStatements postGisDialectStatements(ServiceExtensionContext context) {
        return new PostGisDialectStatements(context.getMonitor());
    }

    @Override
    public void initialize(ServiceExtensionContext context) {
        // Register our decorated converter as the active one.
        // This overrides the previously-registered instance, but still delegates for non-geo criteria.
        context.registerService(FederatedCatalogCacheStatements.class, postGisDialectStatements(context));

        context.getMonitor().info("Registered FederatedCatalogCacheStatements");
    }
}