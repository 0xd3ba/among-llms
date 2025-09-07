from allms.config import AppConfiguration


class Banner:
    """ Class containing the banners for the app """

    # The banner displayed on the main screen
    main_banner = r"""
    ░█▀█░█▄█░█▀█░█▀█░█▀▀░░░█░░░█░░░█▄█░█▀▀░
    ░█▀█░█░█░█░█░█░█░█░█░░░█░░░█░░░█░█░▀▀█░
    ░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░░░▀▀▀░▀▀▀░▀░▀░▀▀▀░
    """

    # The banner displayed on the splash screen
    splash_banner = rf"""
    ╔═╗┌┬┐┌─┐┌┐┌┌─┐  ╦  ╦  ╔╦╗┌─┐
    ╠═╣││││ │││││ ┬  ║  ║  ║║║└─┐
    ╩ ╩┴ ┴└─┘┘└┘└─┘  ╩═╝╩═╝╩ ╩└─┘
    """

    @staticmethod
    def add_border(content: str,
                   additional_lines: list[str] = None,
                   border_char: str = "*",
                   hpad: int = 0,
                   vpad: int = 0,
                   pad_top: bool = True,
                   pad_bottom: bool = True
                   ) -> str:
        """ Helper method to add border to the given content string """
        lines = content.splitlines()
        if additional_lines is not None:
            lines.extend(additional_lines)

        max_len = max(len(line) for line in lines)

        border_width = max_len + 2 * hpad + 2
        top_btm_border = border_char * border_width

        empty_line = f"{border_char}{' ' * (border_width - 2)}{border_char}"
        vpad_lines = [empty_line] * vpad

        # Pad each line horizontally to center text
        padded_lines = []
        for line in lines:
            line = line.strip()
            total_pad = max_len - len(line)
            left_pad = total_pad // 2 + hpad
            right_pad = total_pad - (total_pad // 2) + hpad

            if line:
                padded_lines.append(f"{border_char}{' ' * left_pad}{line}{' ' * right_pad}{border_char}")
            else:
                padded_lines.append(empty_line)

        fmt_lines = [top_btm_border]
        if pad_top:
            fmt_lines += vpad_lines
        fmt_lines += padded_lines
        if pad_bottom:
            fmt_lines += vpad_lines
        fmt_lines += [top_btm_border]

        result = "\n".join(fmt_lines)
        result = "\n" + result + "\n"

        return result
