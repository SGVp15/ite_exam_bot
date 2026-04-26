def filter_lines_txt_file_with_buffer(input_path, output_path, chunk_size=1024 * 1024,
                                      search_query='E:\\'):
    """
    input_path: путь к исходному файлу
    output_path: путь к файлу результата
    chunk_size: размер буфера в байтах (по умолчанию 1 МБ)
    """


    seen_lines = set()
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore', buffering=chunk_size) as infile:
            with open(output_path, 'w', encoding='utf-8', buffering=chunk_size) as outfile:

                while True:
                    lines = infile.readlines(chunk_size)
                    if not lines:
                        break

                    for line in lines:
                        if search_query in line:
                            if line not in seen_lines:
                                outfile.write(line)
                                seen_lines.add(line)

        print(f"Готово! Результат в {output_path}")

    except FileNotFoundError:
        print("Файл не найден.")

input_file = '../copy_log.txt'
output_file = '../1.txt'

filter_lines_txt_file_with_buffer(input_file, output_file)
