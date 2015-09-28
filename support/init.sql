CREATE TABLE `variety` (
  id           BIGINT(20) PRIMARY KEY                                                                                                                       AUTO_INCREMENT,
  name         VARCHAR(64)  NOT NULL DEFAULT '',
  `show_name`  VARCHAR(128) NOT NULL  DEFAULT '',
  `location`   VARCHAR(8)   NOT NULL DEFAULT '',
  `poster`     VARCHAR(255) NOT NULL DEFAULT '',
  `tag`        VARCHAR(128) NOT NULL DEFAULT '',
  `begin_year` SMALLINT     NOT NULL DEFAULT 0,
  `sort`       INT          NOT NULL DEFAULT 0,

  UNIQUE KEY key__unique__name(name)
)
  ENGINE = innodb
  DEFAULT CHARSET utf8;

CREATE TABLE `drama` (
  id             BIGINT(20) PRIMARY KEY                                                                                                                       AUTO_INCREMENT,
  name           VARCHAR(64)  NOT NULL DEFAULT "",
  `poster`       VARCHAR(255) NOT NULL DEFAULT '',
  `actors`       VARCHAR(128) NOT NULL DEFAULT '',
  `description`  VARCHAR(512) NOT NULL DEFAULT '',
  `score`        INT          NOT NULL DEFAULT 0,
  `year`         INT          NOT NULL DEFAULT 0,
  `source`       VARCHAR(128) NOT NULL DEFAULT '',
  `time_created` BIGINT(20)   NOT NULL DEFAULT 0
)
  ENGINE = innodb
  DEFAULT CHARSET utf8;

CREATE TABLE drama_episode (
  id             BIGINT(20) PRIMARY KEY                                                                                                                       AUTO_INCREMENT,
  `drama_id`     BIGINT(20)   NOT NULL DEFAULT 0,
  `episode`      INT          NOT NULL                                                                                                                        DEFAULT 1,
  `time_release` BIGINT(20)   NOT NULL                                                                                                                        DEFAULT 0,
  `poster`       VARCHAR(255) NOT NULL DEFAULT '',
  `source`       VARCHAR(255) NOT NULL DEFAULT '',
  `url`          VARCHAR(512) NOT NULL DEFAULT '',
  `hd_url`       VARCHAR(512) NOT NULL DEFAULT '',
  `detail`       VARCHAR(255) NOT NULL DEFAULT '',

  UNIQUE KEY key__drama_id__episode(drama_id, episode)

)
  ENGINE = innodb
  DEFAULT CHARSET utf8;


CREATE TABLE `url_content` (
  id             BIGINT(20) PRIMARY KEY                                                                                                                       AUTO_INCREMENT,
  `url`          VARCHAR(255) NOT NULL                                                                                                                        DEFAULT '',
  `content_hash` VARCHAR(128) NOT NULL                                                                                                                        DEFAULT '',
  `content`      TEXT DEFAULT NULL,

  UNIQUE KEY ukey__content_hash(content_hash),
  KEY key__url(url)
)
  ENGINE = innodb
  DEFAULT CHARSET utf8;
