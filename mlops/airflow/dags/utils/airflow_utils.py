import magic
import zipfile
import json
import olefile


def make_json_meta_file(data, meta):
    json_data = {}
    with open(meta) as f:
        json_data = json.load(f)

    find_key = ["createdate", "gpslatitude", "gpslongitude"]
    data["text"] += "|"
    data["text"] += json_data["description"]
    if "createdate" in data["metadata"]:
        json_data["datetime"] = data["metadata"]["createdate"]
    else:
        json_data["datetime"] = ""
    if ("gpslatitude" in data["metadata"]) and ("gpslongitude" in data["metadata"]):
        json_data["location"] = (
            f'{data["metadata"]["gpslatitude"], data["metadata"]["gpslongitude"]}'
        )
    else:
        json_data["location"] = ""
    json_data["text"] = data["text"]

    return json_data


def is_doc_ppt_hwp(filepath):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            head = f.read(2048).lower()
            if "<?xml" in head and ("<hwpml" in head or "<hwp>" in head):
                return "hwp"
    except:
        pass

    if not olefile.isOleFile(filepath):
        return False
    try:
        with olefile.OleFileIO(filepath) as ole:
            streams = ole.listdir()
            stream_names = [".".join(s) for s in streams]

            if any("PowerPoint Document" in s for s in stream_names):
                return "ppt"
            elif any("WordDocument" in s for s in stream_names):
                return "doc"
            elif any(
                s in stream_names for s in ["BodyText", "FileHeader", "HwpSummary"]
            ):
                return "hwp"
            else:
                return None
    except:
        pass
    return None


def is_hwpx(filepath):
    try:
        with zipfile.ZipFile(filepath, "r") as zipf:
            names = zipf.namelist()
            if any(name.startswith("Contents/") for name in names):
                return True
    except:
        pass
    return False


def is_pdf(filepath):
    with open(filepath, "rb") as f:
        header = f.read(5)
        return header == b"%PDF-"


def get_file_type_by_magic(filepath):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(filepath)
    spec_file_type = is_doc_ppt_hwp(filepath)
    if is_hwpx(filepath):
        return "hwpx", "text"
    elif filepath.lower().endswith(".csv"):
        return "numerical", "numerical"
    elif mime_type == "application/zip":
        try:
            with zipfile.ZipFile(filepath, "r") as zipf:
                names = [name.replace("\\", "/") for name in zipf.namelist()]
                if any(name.endswith("word/document.xml") for name in names):
                    return "docx", "text"
                elif any(name.endswith("ppt/presentation.xml") for name in names):
                    return "pptx", "text"
                elif any(name.endswith("xl/workbook.xml") for name in names):
                    return "numerical", "numerical"
        except:
            pass
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        try:
            with zipfile.ZipFile(filepath, "r") as zipf:
                names = [name.replace("\\", "/") for name in zipf.namelist()]
                if any(name.endswith("word/document.xml") for name in names):
                    return "docx", "text"
        except:
            pass
    elif (
        mime_type
        == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ):
        try:
            with zipfile.ZipFile(filepath, "r") as zipf:
                names = [name.replace("\\", "/") for name in zipf.namelist()]
                if any(name.endswith("ppt/presentation.xml") for name in names):
                    return "pptx", "text"
        except:
            pass
    elif mime_type.startswith("image/"):
        return "image", "image"
    elif mime_type.startswith("video/"):
        return "video", "video"
    elif mime_type.startswith("audio/"):
        return "audio", "audio"
    elif mime_type == "text/plain":
        return "text", "text"
    elif mime_type in [
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-office",
        "application/xls",
    ]:
        return "numerical", "numerical"
    elif is_pdf(filepath):
        return "pdf", "text"
    elif spec_file_type is not None:
        return spec_file_type, "text"
    else:
        return "text", "text"
