package utils;

public class SqlConfigEditor {
    public static String urlEditor(String url, String port) {
        return "jdbc:mysql://" + url + ":" + port;
    }
}
