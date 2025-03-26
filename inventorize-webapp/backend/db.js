const { Pool } = require('pg');

const pool = new Pool({
  host: 'ep-curly-tooth-ac2lenys-pooler.sa-east-1.aws.neon.tech',
  user: 'neondb_owner',
  password: 'npg_q6Zmhk5JoSxd', 
  database: 'neondb',
  port: 5432,
  ssl: {
    rejectUnauthorized: false
  }
});

module.exports = pool;
