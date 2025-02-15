def capitalize_text(text)
  text.split.map(&:capitalize).join(' ')
end

if ARGV.length != 1
  puts "Usage: ruby text_capitalizer.rb '<input_text>'"
  exit 1
end

input_text = ARGV[0]
result = capitalize_text(input_text)
puts "Capitalized Text: #{result}" 