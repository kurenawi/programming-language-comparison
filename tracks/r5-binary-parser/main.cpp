#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

struct Summary {
  uint32_t total_records = 0;
  uint64_t total_value = 0;
  std::array<uint32_t, 4> type_counts{};
  std::array<uint64_t, 4> type_value_sums{};
  uint32_t flagged_records = 0;
};

static uint16_t read_u16_le(const unsigned char* p) {
  return static_cast<uint16_t>(p[0]) |
         (static_cast<uint16_t>(p[1]) << 8);
}

static uint32_t read_u32_le(const unsigned char* p) {
  return static_cast<uint32_t>(p[0]) |
         (static_cast<uint32_t>(p[1]) << 8) |
         (static_cast<uint32_t>(p[2]) << 16) |
         (static_cast<uint32_t>(p[3]) << 24);
}

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: " << argv[0] << " <frames.bin>\n";
    return 1;
  }

  std::ifstream in(argv[1], std::ios::binary);
  if (!in) {
    std::cerr << "failed to open input\n";
    return 1;
  }

  Summary summary;
  std::array<unsigned char, 8> buf{};

  while (true) {
    in.read(reinterpret_cast<char*>(buf.data()), buf.size());
    std::streamsize n = in.gcount();
    if (n == 0) break;
    if (n != static_cast<std::streamsize>(buf.size())) {
      std::cerr << "truncated record\n";
      return 1;
    }

    uint16_t type = read_u16_le(buf.data());
    uint16_t flags = read_u16_le(buf.data() + 2);
    uint32_t value = read_u32_le(buf.data() + 4);

    if (type == 0 || type >= summary.type_counts.size()) {
      std::cerr << "unsupported record type: " << type << "\n";
      return 1;
    }

    summary.total_records += 1;
    summary.total_value += value;
    summary.type_counts[type] += 1;
    summary.type_value_sums[type] += value;
    if ((flags & 0x1u) != 0) {
      summary.flagged_records += 1;
    }
  }

  std::ostringstream out;
  out << "{";
  out << "\"total_records\":" << summary.total_records << ",";
  out << "\"total_value\":" << summary.total_value << ",";
  out << "\"flagged_records\":" << summary.flagged_records << ",";
  out << "\"type_counts\":{";
  bool first = true;
  for (size_t i = 1; i < summary.type_counts.size(); ++i) {
    if (!first) out << ",";
    first = false;
    out << "\"type_" << i << "\":" << summary.type_counts[i];
  }
  out << "},\"type_value_sums\":{";
  first = true;
  for (size_t i = 1; i < summary.type_value_sums.size(); ++i) {
    if (!first) out << ",";
    first = false;
    out << "\"type_" << i << "\":" << summary.type_value_sums[i];
  }
  out << "}}";

  std::cout << out.str() << "\n";
  return 0;
}
