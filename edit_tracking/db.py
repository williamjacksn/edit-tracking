import datetime
import fort
import uuid

from typing import Dict, List


class Database(fort.PostgresDatabase):
    _version: int = None

    def get_permissions(self, email: str) -> List[str]:
        sql = 'SELECT permissions FROM permissions WHERE email = %(email)s'
        permissions = self.q_val(sql, {'email': email})
        if permissions is None:
            return []
        return sorted(set(permissions.split()))

    def set_permissions(self, email: str, permissions: List[str]):
        params = {'email': email, 'permissions': ' '.join(sorted(set(permissions)))}
        sql = 'DELETE FROM permissions WHERE email = %(email)s'
        self.u(sql, params)
        if permissions:
            sql = 'INSERT INTO permissions (email, permissions) VALUES (%(email)s, %(permissions)s)'
            self.u(sql, params)

    def get_users(self):
        sql = 'SELECT email, permissions FROM permissions ORDER BY email'
        for record in self.q(sql):
            yield {'email': record['email'], 'permissions': record['permissions'].split()}

    def add_edit_tracking(self, params: Dict):
        sql = '''
            INSERT INTO edit_tracking (
                id, created_at, month, year, clin, taskit_number, researchers_edit_number, project, received_on,
                claimed_on, editor, editing_transcription, edit_completed_on, review_completed_on, total_pages, notes
            ) VALUES (
                %(id)s, %(created_at)s, %(month)s, %(year)s, %(clin)s, %(taskit_number)s, %(researchers_edit_number)s,
                %(project)s, %(received_on)s, %(claimed_on)s, %(editor)s, %(editing_transcription)s,
                %(edit_completed_on)s, %(review_completed_on)s, %(total_pages)s, %(notes)s
            ) 
        '''
        params.update({'id': uuid.uuid4(), 'created_at': datetime.datetime.utcnow()})
        self.u(sql, params)

    def delete_edit_tracking(self, record_id: uuid.UUID):
        sql = 'DELETE FROM edit_tracking WHERE id = %(id)s'
        params = {'id': record_id}
        self.u(sql, params)

    def get_edit_tracking(self) -> List[Dict]:
        sql = '''
            SELECT
                id, created_at, month, year, clin, taskit_number, researchers_edit_number, project, received_on,
                claimed_on, editor, editing_transcription, edit_completed_on, review_completed_on, total_pages, notes
            FROM edit_tracking
            ORDER BY created_at DESC
        '''
        return self.q(sql)

    def update_edit_tracking(self, params: Dict):
        sql = '''
            UPDATE edit_tracking
            SET month = %(month)s, year = %(year)s, clin = %(clin)s, taskit_number = %(taskit_number)s,
                researchers_edit_number = %(researchers_edit_number)s, project = %(project)s,
                received_on = %(received_on)s, claimed_on = %(claimed_on)s, editor = %(editor)s,
                editing_transcription = %(editing_transcription)s, edit_completed_on = %(edit_completed_on)s,
                review_completed_on = %(review_completed_on)s, total_pages = %(total_pages)s, notes = %(notes)s
            WHERE id = %(id)s
        '''
        self.u(sql, params)

    def _table_exists(self, table_name: str) -> bool:
        sql = 'SELECT count(*) table_count FROM information_schema.tables WHERE table_name = %(table_name)s'
        for record in self.q(sql, {'table_name': table_name}):
            if record['table_count'] == 0:
                return False
        return True

    @property
    def version(self) -> int:
        if self._version is None:
            self._version = 0
            if self._table_exists('schema_versions'):
                sql = 'SELECT max(schema_version) current_version FROM schema_versions'
                current_version: int = self.q_val(sql)
                if current_version is not None:
                    self._version = current_version
        return self._version

    def add_schema_version(self, schema_version: int):
        self._version = schema_version
        sql = '''
            INSERT INTO schema_versions (schema_version, migration_timestamp)
            VALUES (%(schema_version)s, %(migration_timestamp)s)
        '''
        params = {
            'migration_timestamp': datetime.datetime.utcnow(),
            'schema_version': schema_version
        }
        self.u(sql, params)

    def migrate(self):
        self.log.info(f'Database schema version is {self.version}')
        if self.version < 1:
            self.log.info('Migrating database to schema version 1')
            self.u('''
                CREATE TABLE schema_versions (
                    schema_version integer PRIMARY KEY,
                    migration_timestamp timestamp
                )
            ''')
            self.u('''
                CREATE TABLE permissions (
                    email text PRIMARY KEY,
                    permissions text
                )
            ''')
            self.u('''
                CREATE TABLE edit_tracking (
                    id uuid PRIMARY KEY,
                    created_at timestamp,
                    month text,
                    year integer,
                    clin integer,
                    taskit_number text,
                    researchers_edit_number text,
                    project text,
                    received_on date,
                    claimed_on date,
                    editor text,
                    editing_transcription text,
                    edit_completed_on date,
                    review_completed_on date,
                    total_pages integer,
                    notes text
                )
            ''')
            self.add_schema_version(1)
