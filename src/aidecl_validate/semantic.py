from datetime import date, datetime


def validate_semantics(data, verbose=False):
    """Run semantic validation rules on parsed aidecl data.

    Returns (warnings, errors) where each is a list of strings.
    """
    warnings = []
    errors = []

    ai = data.get("ai_usage", {})
    used = ai.get("used")
    tools = ai.get("tools", [])
    level = ai.get("level")

    # rule 1: used=true but no tools listed
    if used is True and len(tools) == 0:
        warnings.append("AI usage declared but no tools listed")

    # rule 2: used=false but tools present
    if used is False and len(tools) > 0:
        errors.append("used is false but tools are listed")

    # rule 3: used=false but level is not none
    if used is False and level is not None and level != "none":
        errors.append("used is false but level is '{}', expected 'none'".format(level))

    # rule 4: code_proportion sum check
    prop = ai.get("code_proportion", {})
    if prop:
        gen = prop.get("ai_generated_percent", 0)
        assisted = prop.get("ai_assisted_percent", 0)
        human = prop.get("human_only_percent", 0)
        total = gen + assisted + human
        if total > 0 and abs(total - 100) > 5:
            warnings.append(
                "code_proportion percentages sum to {} (expected ~100)".format(total)
            )

    # rule 5: declaration date in the future
    decl = data.get("declaration", {})
    decl_date = _parse_date(decl.get("date"))
    if decl_date and decl_date > date.today():
        warnings.append("declaration date is in the future: {}".format(decl.get("date")))

    # rule 6: review_date before declaration date
    review_dt = _parse_date(decl.get("review_date"))
    if review_dt and decl_date and review_dt > decl_date:
        warnings.append("review_date ({}) is after declaration date ({})".format(
            decl.get("review_date"), decl.get("date")))

    # rule 7: review_performed but no review_type
    sec = data.get("security", {})
    if sec.get("review_performed") is True and not sec.get("review_type"):
        warnings.append("security review performed but no review_type specified")

    # rule 8: personal data sent without DPIA
    dh = data.get("data_handling", {})
    if dh.get("personal_data_sent") is True and not dh.get("dpa_completed"):
        warnings.append("personal data sent to AI tools but no DPA completed")

    # rule 9: extensive level but no proportion data
    if level == "extensive" and not prop:
        warnings.append("level is 'extensive' but no code_proportion provided")

    # rule 10: component tools not in tools list
    tool_names = {t.get("name") for t in tools if t.get("name")}
    for comp in ai.get("components", []):
        for tname in comp.get("tools_used", []):
            if tname not in tool_names:
                warnings.append(
                    "component '{}' references tool '{}' not in tools list".format(
                        comp.get("name", "?"), tname))

    # rule 11: schema version check
    sv = data.get("schema_version", "")
    if sv and sv > "1.0.0":
        warnings.append(
            "file declares schema version {} which is newer than supported 1.0.0".format(sv))

    # rule 12: tool period end before start
    for tool in tools:
        period = tool.get("period", {})
        start = _parse_date(period.get("start"))
        end = _parse_date(period.get("end"))
        if start and end and end < start:
            errors.append("tool '{}' has period end ({}) before start ({})".format(
                tool.get("name", "?"), period.get("end"), period.get("start")))

    # rule 13: trains_on_data without data_handling
    for tool in tools:
        if tool.get("trains_on_data") is True and not data.get("data_handling"):
            warnings.append(
                "tool '{}' trains on data but no data_handling section present".format(
                    tool.get("name", "?")))

    # rule 14: next_review in the past
    next_rev = _parse_date(decl.get("next_review"))
    if next_rev and next_rev < date.today():
        warnings.append("next_review date ({}) is in the past, declaration may be overdue for review".format(
            decl.get("next_review")))

    return warnings, errors


def _parse_date(val):
    if not val or not isinstance(val, str):
        return None
    try:
        return datetime.strptime(val, "%Y-%m-%d").date()
    except ValueError:
        return None
