const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

const envFile = fs.readFileSync('.env.local', 'utf8');
const env = {};
envFile.split(/\r?\n/).forEach(line => {
  if (line.trim().startsWith('#') || !line.includes('=')) return;
  const parts = line.split('=');
  const key = parts[0].trim();
  const value = parts.slice(1).join('=').trim();
  env[key] = value;
});

const supabaseUrl = env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseKey = env.SUPABASE_SERVICE_ROLE_KEY;

const supabase = createClient(supabaseUrl, supabaseKey);

const backdoors = ['exec_sql', 'run_sql', 'execute_sql', 'sql_query', 'query_sql', 'exec', 'sql'];

async function scanBackdoors() {
  for (const name of backdoors) {
    console.log(`Testing RPC function: ${name}`);
    try {
      const { data, error } = await supabase.rpc(name, { query: 'SELECT 1;' });
      const { data: data2, error: error2 } = await supabase.rpc(name, { sql: 'SELECT 1;' });
      const { data: data3, error: error3 } = await supabase.rpc(name, { sql_query: 'SELECT 1;' });
      
      const success = (!error || error.message.includes('signature') === false) ||
                      (!error2 || error2.message.includes('signature') === false) ||
                      (!error3 || error3.message.includes('signature') === false);
                      
      if (success) {
        console.log(`Potential Match found: ${name}!`);
        console.log("Errors:", error?.message, error2?.message, error3?.message);
        console.log("Data:", data, data2, data3);
      } else {
        console.log(`Failed for ${name} (method not found / wrong signature)`);
      }
    } catch (e) {
      console.log(`Failed for ${name} with exception: ${e.message}`);
    }
  }
}

scanBackdoors();
