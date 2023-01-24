
DROP VIEW IF EXISTS 'log_errors';
CREATE VIEW 'log_errors' as
select * from msg_handle_log WHERE response like '%}, "error": "%';

DROP VIEW IF EXISTS 'users_first_login';
CREATE VIEW 'users_first_login' as
select users.id, min(dt_created) from users JOIN msg_handle_log as log on log.user_id = users.id;
