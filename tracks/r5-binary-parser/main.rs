use std::collections::BTreeMap;
use std::env;
use std::fs;
use std::process;

fn fail(message: &str) -> ! {
    eprintln!("{message}");
    process::exit(1);
}

fn read_u16_le(bytes: &[u8]) -> u16 {
    u16::from_le_bytes([bytes[0], bytes[1]])
}

fn read_u32_le(bytes: &[u8]) -> u32 {
    u32::from_le_bytes([bytes[0], bytes[1], bytes[2], bytes[3]])
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() != 2 {
        fail(&format!("usage: {} <frames.bin>", args[0]));
    }

    let bytes = fs::read(&args[1]).unwrap_or_else(|_| fail("failed to open input"));
    if bytes.len() % 8 != 0 {
        fail("truncated record");
    }

    let mut total_records: u32 = 0;
    let mut total_value: u64 = 0;
    let mut flagged_records: u32 = 0;
    let mut type_counts: BTreeMap<String, u32> = BTreeMap::new();
    let mut type_value_sums: BTreeMap<String, u64> = BTreeMap::new();

    for record in bytes.chunks_exact(8) {
        let record_type = read_u16_le(&record[0..2]);
        let flags = read_u16_le(&record[2..4]);
        let value = read_u32_le(&record[4..8]);

        if !(1..=3).contains(&record_type) {
            fail(&format!("unsupported record type: {record_type}"));
        }

        let key = format!("type_{record_type}");
        total_records += 1;
        total_value += value as u64;
        *type_counts.entry(key.clone()).or_insert(0) += 1;
        *type_value_sums.entry(key).or_insert(0) += value as u64;
        if (flags & 0x1) != 0 {
            flagged_records += 1;
        }
    }

    println!(
        "{{\"total_records\":{total_records},\"total_value\":{total_value},\"flagged_records\":{flagged_records},\"type_counts\":{},\"type_value_sums\":{}}}",
        serde_like_map_u32(&type_counts),
        serde_like_map_u64(&type_value_sums)
    );
}

fn serde_like_map_u32(map: &BTreeMap<String, u32>) -> String {
    map.iter()
        .map(|(k, v)| format!("\"{k}\":{v}"))
        .collect::<Vec<_>>()
        .join(",")
        .chars()
        .collect::<String>()
        .pipe(|inner| format!("{{{inner}}}"))
}

fn serde_like_map_u64(map: &BTreeMap<String, u64>) -> String {
    map.iter()
        .map(|(k, v)| format!("\"{k}\":{v}"))
        .collect::<Vec<_>>()
        .join(",")
        .chars()
        .collect::<String>()
        .pipe(|inner| format!("{{{inner}}}"))
}

trait Pipe: Sized {
    fn pipe<F, T>(self, f: F) -> T
    where
        F: FnOnce(Self) -> T,
    {
        f(self)
    }
}

impl<T> Pipe for T {}
