package mapper;

import model.SqlHandler;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;

public class DataMapper {

    public static List<Map<String, Object>> getAllData(SqlHandler sqlHandler, String db, String tb) throws SQLException {
        return sqlHandler.execute("SELECT * FROM " + db + "." + tb);
    }
}
