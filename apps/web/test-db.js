const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');

// Read and parse .env.local manually to ensure perfect loading
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
const supabaseAnonKey = env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log("Supabase URL:", supabaseUrl);
console.log("Supabase Anon Key present:", !!supabaseAnonKey);

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing credentials in .env.local");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  console.log("Attempting table query to Supabase...");
  const start = Date.now();
  try {
    const { data, error } = await supabase.from('users').select('id, email').limit(2);
    console.log(`Finished in ${Date.now() - start}ms`);
    if (error) {
      console.error("Query Error:", error);
    } else {
      console.log("Connection successful! Query data:", JSON.stringify(data));
    }
  } catch (e) {
    console.error("Exception during connection:", e);
  }
}

testConnection();
