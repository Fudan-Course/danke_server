INSERT INTO user (username, email, password, description, nickname, code) VALUES ('alice', 'alice@fudan.edu.cn', '123456','testA', 'alice', ''), ('bob', 'bob@fudan.edu.cn', '123456','testB', 'bob', ''), ('cube', 'cube@fudan.edu.cn', '123456','testC', 'cube', '');

INSERT INTO session (id, user_id, login_time, expiration_time) VALUES ('1111111111', 1, 1573051148, 1577777777), ('2222222222', 2, 1573051148, 1577777777), ('3333333333', 3, 1573051148, 1577777777);