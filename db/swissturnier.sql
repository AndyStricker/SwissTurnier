--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Table category
--

CREATE SEQUENCE category_id_category_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE category (
    id_category integer NOT NULL DEFAULT nextval('category_id_category_seq'),
    name text NOT NULL
);

ALTER TABLE public.category OWNER TO stuser;
ALTER TABLE ONLY category
    ADD CONSTRAINT category_pkey PRIMARY KEY (id_category);
ALTER TABLE ONLY category
    ADD CONSTRAINT name_key UNIQUE (name);
ALTER TABLE public.category_id_category_seq OWNER TO stuser;
ALTER SEQUENCE category_id_category_seq OWNED BY category.id_category;


--
-- Table Team
--

CREATE SEQUENCE team_id_team_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE team (
    id_team integer NOT NULL DEFAULT nextval('team_id_team_seq'),
    name text NOT NULL,
    id_category integer NOT NULL
);

ALTER TABLE public.team OWNER TO stuser;
ALTER TABLE ONLY team
    ADD CONSTRAINT team_pkey PRIMARY KEY (id_team);
ALTER TABLE ONLY team
    ADD CONSTRAINT team_name_key UNIQUE (name);
ALTER TABLE ONLY team
    ADD CONSTRAINT team_category_fkey FOREIGN KEY (id_category) REFERENCES category(id_category);
ALTER TABLE public.team_id_team_seq OWNER TO stuser;
ALTER SEQUENCE team_id_team_seq OWNED BY team.id_team;

--
-- Table playround
--

CREATE SEQUENCE playround_id_playround_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE playround (
    id_playround integer NOT NULL DEFAULT nextval('playround_id_playround_seq'),
    round_number integer NOT NULL,
    id_team_a integer NOT NULL,
    id_team_b integer,
    points_a integer,
    points_b integer
);

ALTER TABLE public.playround OWNER TO stuser;
ALTER TABLE ONLY playround
    ADD CONSTRAINT playround_pkey PRIMARY KEY (id_playround);
ALTER TABLE ONLY playround
    ADD CONSTRAINT round_number_key UNIQUE (round_number);
ALTER TABLE ONLY playround
    ADD CONSTRAINT playround_id_team_a_fkey FOREIGN KEY (id_team_a) REFERENCES team(id_team);
ALTER TABLE ONLY playround
    ADD CONSTRAINT playround_id_team_b_fkey FOREIGN KEY (id_team_b) REFERENCES team(id_team);
ALTER TABLE public.playround_id_playround_seq OWNER TO stuser;
ALTER SEQUENCE playround_id_playround_seq OWNED BY playround.id_playround;

--
-- Table rankings
--

CREATE SEQUENCE rankings_id_rankings_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE rankings (
    id_rank integer NOT NULL DEFAULT nextval('rankings_id_rankings_seq'),
    id_team integer NOT NULL,
    rank integer,
    wins float,
    points integer
);

ALTER TABLE public.rankings OWNER TO stuser;

ALTER TABLE ONLY rankings
    ADD CONSTRAINT rankings_pkey PRIMARY KEY (id_rank);
ALTER TABLE ONLY rankings
    ADD CONSTRAINT id_team_key UNIQUE (id_team);
ALTER TABLE ONLY rankings
    ADD CONSTRAINT rankings_id_team_fkey FOREIGN KEY (id_team) REFERENCES team(id_team);
ALTER TABLE public.rankings_id_rankings_seq OWNER TO stuser;
ALTER SEQUENCE rankings_id_rankings_seq OWNED BY rankings.id_rank;

--
-- PostgreSQL database create
--

