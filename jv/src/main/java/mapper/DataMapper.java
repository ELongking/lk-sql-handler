package mapper;

import model.CommonResult;
import model.SqlHandler;
import utils.LogUtil;
import utils.SqlEditor;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

public class DataMapper {

    public static List<Map<String, Object>> getAllData(SqlHandler sqlHandler, String db, String tb) throws SQLException {
        return sqlHandler.execute("SELECT * FROM " + db + "." + tb);
    }

    public static CommonResult<List<Map<String, Object>>> updateData(
            SqlHandler sqlHandler,
            List<List<String>> data,
            List<List<String>> pkey,
            String db,
            String tb) {

        String value_str = "", pkey_str = "";
        for (List<String> group : data) {
            String ans = String.format("`%s` = %s,", group.get(0), group.get(1));
            value_str += ans;
        }
        for (List<String> group : pkey) {
            String ans = String.format("`%s` = %s,", group.get(0), group.get(1));
            pkey_str += ans;
        }
        String sql = String.format("UPDATE `%s`.`%s` SET %s WHERE %s;", db, tb, value_str, pkey_str);
        LogUtil.info("sql sentence => " + sql);

        try {
            List<Map<String, Object>> sqlRes = sqlHandler.execute(sql);
            return SqlEditor.rawResultEnhance(sqlRes);
        } catch (SQLException e) {
            LogUtil.error("sql error =>", e);
            return SqlEditor.rawResultEnhance(e);
        }
    }

    public static CommonResult<List<Map<String, Object>>> insertData(
            SqlHandler sqlHandler,
            List<List<String>> data,
            List<List<String>> pkey,
            String db,
            String tb) {

        String value_str = "", pkey_str = "";
        for (List<String> group : data) {
            String ans = String.format("`%s` = %s,", group.get(0), group.get(1));
            value_str += ans;
        }
        for (List<String> group : pkey) {
            String ans = String.format("`%s` = %s,", group.get(0), group.get(1));
            pkey_str += ans;
        }
        String sql = String.format("INSERT `%s`.`%s` SET %s WHERE %s;", db, tb, value_str, pkey_str);
        LogUtil.info("sql sentence => " + sql);

        try {
            List<Map<String, Object>> sqlRes = sqlHandler.execute(sql);
            return SqlEditor.rawResultEnhance(sqlRes);
        } catch (SQLException e) {
            LogUtil.error("sql error =>", e);
            return SqlEditor.rawResultEnhance(e);
        }

    }

}
