INSERT INTO user (name, email, password, description, nickname, code) VALUES ('admin', 'admin@danke.com', '123456','admin', 'admin', '');
INSERT INTO user_permission (user_id, permission_type) VALUES (1, 1);
INSERT INTO forum (title, is_locked, only_admin, cmp_key, count_topics) VALUES ('旦课', true, true, 0, 0);