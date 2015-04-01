from pystratum.RoutineLoader import RoutineLoader
from pystratum.mssql.MsSqlRoutineLoaderHelper import MsSqlRoutineLoaderHelper
from pystratum.mssql.StaticDataLayer import StaticDataLayer


# ----------------------------------------------------------------------------------------------------------------------
class MsSqlRoutineLoader(RoutineLoader):
    """
    Class for loading stored routines into a MySQL instance from pseudo SQL files.
    """
    # ------------------------------------------------------------------------------------------------------------------
    def connect(self):
        """
        Connects to the database.
        """
        StaticDataLayer.connect(self._host_name,
                                self._user_name,
                                self._password,
                                self._database)

    # ------------------------------------------------------------------------------------------------------------------
    def disconnect(self):
        """
        Disconnects from the database.
        """
        StaticDataLayer.disconnect()

    # ------------------------------------------------------------------------------------------------------------------
    def _get_column_type(self):
        """
        Selects schema, table, column names and the column types from the SQL Server instance and saves them as replace
        pairs.
        """
        sql = """
select scm.name  schema_name
,      tab.name  table_name
,      col.name  column_name
,      typ.name  data_type
,      col.max_length
,      col.precision
,      col.scale
from sys.columns                  col
inner join sys.types              typ  on  col.user_type_id = typ.user_type_id
inner join sys.tables             tab  on  col.[object_id] = tab.[object_id]
inner join sys.schemas            scm  on  tab.[schema_id] = scm.[schema_id]
where tab.type in ('U','S','V')
order by  scm.name
,         tab.name
,         col.column_id"""

        rows = StaticDataLayer.execute_rows(sql)

        for row in rows:
            key = '@'
            if row['schema_name']:
                key += row['schema_name'] + '.'
            key += row['table_name'] + '.' + row['column_name'] + '%type@'
            key = key.lower()

            value = self._derive_data_type(row)

            self._replace_pairs[key] = value

    # ------------------------------------------------------------------------------------------------------------------
    def create_routine_loader_helper(self,
                                     routine_name: str,
                                     old_metadata: dict,
                                     old_routine_info: dict) -> MsSqlRoutineLoaderHelper:
        """
        Factory for creating a Routine Loader Helper objects (i.e. objects loading a single stored routine into a RDBMS
        instance from a (pseudo) SQL file).
        :return:
        """
        return MsSqlRoutineLoaderHelper(self._source_file_names[routine_name],
                                        self._source_file_extension,
                                        old_metadata,
                                        self._replace_pairs,
                                        old_routine_info)

    # ------------------------------------------------------------------------------------------------------------------
    def _get_old_stored_routine_info(self):
        """
        Retrieves information about all stored routines in the current schema.
        """
        query = """
select scm.name  schema_name
,      prc.name  procedure_name
,      prc.[type]  [type]
from       sys.all_objects  prc
inner join sys.schemas     scm  on   scm.schema_id = prc.schema_id
where prc.type in ('P','FN')
and   scm.name <> 'sys'
and   prc.is_ms_shipped=0"""

        rows = StaticDataLayer.execute_rows(query)

        self._old_stored_routines_info = {}
        for row in rows:
            self._old_stored_routines_info[row['procedure_name']] = row

    # ------------------------------------------------------------------------------------------------------------------
    def _drop_obsolete_routines(self):
        """
        Drops obsolete stored routines (i.e. stored routines that exits in the current schema but for
        which we don't have a source file).
        """
        for routine_name, values in self._old_stored_routines_info.items():
            if routine_name not in self._source_file_names:
                # todo improve drop fun and proc
                print("Dropping %s.%s" % (values['schema_name'], routine_name))
                sql = "drop procedure %s.%s" % (values['schema_name'], routine_name)
                StaticDataLayer.execute_none(sql)

    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def _derive_data_type(column: dict) -> int:
        """
        Returns the proper SQL declaration of a data type of a column.
        :param column dict The column of which the field is based.
        :returns SQL declaration of data type
        """
        data_type = column['data_type']

        if data_type == 'bigint':
            return data_type

        if data_type == 'int':
            return data_type

        if data_type == 'smallint':
            return data_type

        if data_type == 'tinyint':
            return data_type

        if data_type == 'bit':
            return data_type

        if data_type == 'money':
            return data_type

        if data_type == 'smallmoney':
            return data_type

        if data_type == 'decimal':
            return 'decimal(%d,%d)' % (column['precision'], column['scale'])

        if data_type == 'numeric':
            return 'decimal(%d,%d)' % (column['precision'], column['scale'])

        if data_type == 'float':
            return data_type

        if data_type == 'real':
            return data_type

        if data_type == 'date':
            return data_type

        if data_type == 'datetime':
            return data_type

        if data_type == 'datetime2':
            return data_type

        if data_type == 'datetimeoffset':
            return data_type

        if data_type == 'smalldatetime':
            return data_type

        if data_type == 'time':
            return data_type

        if data_type == 'char':
            return 'char(%d)' % column['max_length']

        if data_type == 'varchar':
            if column['max_length'] == -1:
                return 'varchar(max)'

            return 'varchar(%d)' % column['max_length']

        if data_type == 'text':
            return data_type

        if data_type == 'nchar':
            return 'nchar(%d)' % (column['max_length'] / 2)

        if data_type == 'nvarchar':
            if column['max_length'] == -1:
                return 'nvarchar(max)'

            return 'nvarchar(%d)' % (column['max_length'] / 2)

        if data_type == 'ntext':
            return data_type

        if data_type == 'binary':
            return data_type

        if data_type == 'varbinary':
            return 'varbinary(%d)' % column['max_length']

        if data_type == 'image':
            return data_type

        if data_type == 'xml':
            return data_type

        if data_type == 'geography':
            return data_type

        if data_type == 'geometry':
            return data_type

        raise Exception("Unexpected data type '%s'." % data_type)


# ----------------------------------------------------------------------------------------------------------------------

