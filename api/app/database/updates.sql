CREATE TYPE public.userkpilevelsorm AS ENUM (
	'TRAINEE',
	'SPECIALIST',
	'EXPERT',
	'TOP');
	
CREATE TABLE last_month_statistics_with_kpi (
    user_id int4 NOT NULL,
    flyers int4 NOT NULL DEFAULT 0,
    calls int4 NOT NULL DEFAULT 0,
    shows int4 NOT NULL DEFAULT 0,
    meets int4 NOT NULL DEFAULT 0,
    deals int4 NOT NULL DEFAULT 0,
    deposits int4 NOT NULL DEFAULT 0,
    searches int4 NOT NULL DEFAULT 0,
    analytics int4 NOT NULL DEFAULT 0,
    others int4 NOT NULL DEFAULT 0,
    user_level public."userkpilevelsorm" not null,
    salary_percentage FLOAT DEFAULT 0.0,
    CONSTRAINT last_month_statistics_with_kpi_pkey PRIMARY KEY (user_id),
	CONSTRAINT last_month_statistics_with_kpi_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE
);

select * from last_month_statistics_with_kpi;

INSERT INTO last_month_statistics_with_kpi (user_id, flyers, calls, shows, meets, deals, deposits, searches, analytics, others, user_level, salary_percentage)
SELECT user_id, flyers, calls, shows, meets, deals, deposits, searches, analytics, others, 'TRAINEE', 100.0
FROM month_statistics;


create table images(
	id serial4 not null primary key,
	"name" varchar(200),
	"data" bytea
);

insert into images(name, data) values ('default_image', null);
select * from users;

alter table users 
add column image int4 not null default 1, 
add constraint fk_user_image foreign key (image) references images(id);


create table calls_records(
	id serial4 not null primary key,
	"name" varchar(200),
	"data" bytea
);

create table users_calls(
	user_id int4 NOT null,
	record_id int4 not null,
	info varchar null,
	date_time int4 not null,
	phone_number varchar not null,
	transcription varchar default 'no transcription',
	constraint users_calls_pk primary key (user_id, record_id),
	CONSTRAINT users_calls_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE cascade,
	CONSTRAINT users_calls_record_id_fkey FOREIGN KEY (record_id) REFERENCES public.calls_records(id) ON DELETE CASCADE
);











