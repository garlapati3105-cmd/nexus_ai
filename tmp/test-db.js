const { createClient } = require('@supabase/supabase-js');
require('dotenv').config({ path: 'apps/web/.env.local' });

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

console.log("Supabase URL:", supabaseUrl);
console.log("Supabase Anon Key present:", !!supabaseAnonKey);

if (!supabaseUrl || !supabaseAnonKey) {
  console.error("Missing credentials in apps/web/.env.local");
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  console.log("Attempting connection to Supabase...");
  const start = Date.now();
  try {
    const { data, error } = await supabase.from('users').select('count', { count: 'exact', head: true });
    console.log(`Finished in ${Date.now() - start}ms`);
    if (error) {
      console.error("Query Error:", error);
    } else {
      console.log("Connection successful! User count:", data);
    }
  } catch (e) {
    console.error("Exception during connection:", e);
  }
}

testConnection();
