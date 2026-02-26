package psnc;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.eclipse.edc.spi.monitor.Monitor;
import org.eclipse.edc.spi.query.QuerySpec;
import org.eclipse.edc.sql.dialect.PostgresDialect;
import org.eclipse.edc.sql.translation.PostgresqlOperatorTranslator;
import org.eclipse.edc.sql.translation.SqlQueryStatement;
import org.eclipse.edc.catalog.cache.sql.BaseSqlDialectStatements;
import org.eclipse.edc.catalog.cache.sql.schema.postgres.PostgresDialectStatements;
import static java.lang.String.format;

public class PostGisDialectStatements extends BaseSqlDialectStatements {

    public static final String GEO_PREFIX = "geo";
    public static final String GEO_COVERS_POINT = "geo:coversPoint";

    private PostgresDialectStatements statements;

    private Monitor monitor;

    public PostGisDialectStatements(Monitor monitor) {
        super(new PostgresqlOperatorTranslator());

        this.monitor = monitor;
        this.statements = new PostgresDialectStatements();
    }

    @Override
    public String getFormatAsJsonOperator() {
        return PostgresDialect.getJsonCastOperator();
    }

    @Override
    public SqlQueryStatement createQuery(QuerySpec querySpec) {

        var filteringExpressions = querySpec.getFilterExpression();

        var isGeoSpatial = false;
        for (var item : filteringExpressions) {
            if (item.getOperator().startsWith(GEO_PREFIX)) {
                isGeoSpatial = true;
            }
        }

        monitor.info("Is geospatial");
        monitor.info(Boolean.toString(isGeoSpatial));

        if (isGeoSpatial) {
            return getPostGisQuery(querySpec);
        } else {
            return statements.createQuery(querySpec);
        }
    }

    private SqlQueryStatement getPostGisQuery(QuerySpec querySpec) {

        var query = format("SELECT * FROM %s", getFederatedCatalogTable());
        monitor.info(query);

        var queryObj = new SqlQueryStatement(query, querySpec.getLimit(), querySpec.getOffset());

        return queryObj;
    }
}