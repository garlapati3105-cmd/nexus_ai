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
const supabaseKey = env.SUPABASE_SERVICE_ROLE_KEY; // use service role key to bypass RLS

const supabase = createClient(supabaseUrl, supabaseKey);

async function testInventory() {
  try {
    const { data: invData, error: invErr } = await supabase.from('inventory').select('*').limit(1);
    if (invData && invData.length > 0) {
      console.log("Inventory keys:", Object.keys(invData[0]));
      console.log("Inventory full row:", JSON.stringify(invData[0], null, 2));
    } else {
      console.log("No inventory data, error:", invErr);
    }
    
    const { data: branchData, error: branchErr } = await supabase.from('branches').select('*').limit(1);
    if (branchData && branchData.length > 0) {
      console.log("Branches keys:", Object.keys(branchData[0]));
    } else {
      console.log("No branch data, error:", branchErr);
    }
  } catch (e) {
    console.error("Exception:", e);
  }
}

testInventory();
