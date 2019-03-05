const int OP_ADD_COMMENT = 0;
const int OP_SET_STATE = 1;

void dump_tracing_step()
{
    end_tracing_step();
    trace_flush();
    begin_tracing_step();
    maybe_reopen_trace_file();
}
void begin_tracing_step()
{
    trace_write_raw("S([");
}
void end_tracing_step()
{
    trace_write_raw("]);");
}
void proof_trace_add_op(json &op)
{
    string msg;
    op.dump(msg/*, jsoncons::indenting::indent*/);
    msg += ",";
    trace_write_raw(msg);
}
void proof_trace_set_comment(state_id id, const string &comment)
{
    /*json op;
    op["a"] = "set_comment";
    op["id"] = id;
    op["comment"] = comment;*/
    json op = json::array();
    op.push_back(OP_ADD_COMMENT);
    op.push_back(id);
    op.push_back(comment);
    proof_trace_add_op(op);
}
void proof_trace_set_status(state_id id, coro_status status, bool with_introduction, state_id parent_id, RuleId rule_id, Thing* locals_address, string *comment)
{
    /*json op;
    op["a"] = "set_status";
    op["id"] = id;
    op["status"] = (int)status;
    */
    json op = json::array();
    op.push_back(OP_SET_STATE);
    op.push_back(id);
    op.push_back((int)status);
    if (with_introduction)
    {
        //op["parent_id"] = parent_id;
        op.push_back(parent_id);
        op.push_back(rule_id);
        op.push_back((size_t)locals_address);
        //remove when rule descriptions are taken from the json
        if (comment)
        {
            //op["comment"] = *comment;
            op.push_back(*comment);
        }
    }
    proof_trace_add_op(op);
}
void proof_trace_emit_euler_steps()
{
    json op;
    op["a"] = "set_steps";
    op["value"] = euler_steps;
    proof_trace_add_op(op);
}

void trace_write_raw(string s)
{
    trace_string += s;
}
void open_trace_file()
{
    written_bytes = 0;
    trace.open(trace_output_path"/trace" + to_string(current_trace_file_id) + ".js");
    //trace_write_raw("window.pyco = Object();window.pyco.frames = [];");//??
    //dump();

    begin_tracing_step();

    static chrono::steady_clock::time_point tp = std::chrono::steady_clock::now();
    auto uuid = chrono::time_point_cast<std::chrono::milliseconds>(tp).time_since_epoch().count();
    json op;
    op["a"] = "run_uuid";
    op["value"] = uuid;
    proof_trace_add_op(op);
}
void trace_flush()
{
    written_bytes += trace_string.size();
    trace << trace_string << endl;
    trace_string.clear();
    /*trace.close();trace.open(trace_output_path"/trace.js", ios_base::app);*/
}
void close_trace_file()
{
    end_tracing_step();
    trace_flush();
    trace.close();
}
void maybe_reopen_trace_file()
{
    if (written_bytes / (1024*1024*5))
    {
        close_trace_file();
        current_trace_file_id++;
        open_trace_file();
    }
}
