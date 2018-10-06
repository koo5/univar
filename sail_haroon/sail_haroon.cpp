enum ThingType
{
	bound = 0;
	unbound = 1;
	constant = 2;
	unbound_bnode = 3;
	bound_bnode = 4;
	list = 5;
};

class Thing
{
	ThingType type;




};

class Frame{
	parent
	depth
	Frame *children;
	Thing locals;

};


void everything()
{
func_start:
create_and_try_generator:

	if (frame.depth < frame.rule.args_len)
		{
			source = frame.args[depth];
			target = frame.locals[depth];
			GeneratorPointer generator = unify(source, target);
			if (generator.type() == failed)


			head_thing.arg_index = arg_index
		elif len(incoming_bnode_unifications):
			assert depth < len(args) + len(incoming_bnode_unifications)
			ua,ub = incoming_bnode_unifications[depth - len(args)]
			generator = unify(ua, ub)
		else:
			assert depth < len(args) + len(singleton.body)
			body_item_index = depth - len(args)
			triple = singleton.body[body_item_index]
			bi_args = []
			for arg_idx, uri in enumerate(triple.args):
			thing = locals[uri]
			bi_args.append(Arg(uri, get_value(thing), thing.debug_locals().kbdbg_frame, body_item_index, arg_idx, False))
			generator = pred(triple.pred, kbdbg_name, bi_args)

		frame.generators[depth] = generator;
		frame.generators_len ++;

try_generator:
		frame = frame.generators[depth];
		generators[depth].__next__()

generator_failed_quickly:
		if (frame.depth-- == 0)
			goto rule_done;
		g = frame.generators[depth];
		if (g < 256)
			goto func_start + g;
		frame = g;
		goto continue_complex_unification;
new_generator_succeeded:
		frame.generators[depth] = new_generator;
generator_succeeded:
		if depth == len(args) - 1:
			incoming_bnode_unifications = []
			for k,v in locals.items():
				vv = get_value(v)
				if vv != v and type(vv) == Var and vv.bnode() and vv.is_a_bnode_from_original_rule == singleton.original_head and k == vv.is_from_name:
				log('its a bnode')
				b = vv.bnode()
				for k,v in b.items():
				if not is_var(k): continue
				incoming_bnode_unifications.append((
				Arg(k, locals[k], locals.kbdbg_name, k, 0, 'bnode'),
				Arg(k, b[k], b.kbdbg_name, k, 0, 'bnode')))

			if len(incoming_bnode_unifications):
			max_depth = len(args) + len(incoming_bnode_unifications) - 1
			depth++;
			goto create_generator;
			else:
			max_depth = len(args) + len(singleton.body) - 1
		
		if (++depth < max_depth):
			goto create_generator;
		else:
			frame.next_state = try_generator;
			frame = frame.parent;
			goto on_child_success;



unify:
		if (unification_source.type() == bound)
		{
			if (unification_target.type() == bound)
				unification_source,unification_target = get_value_multi(unification_source.bound_to(),unification_target.bound_to());
			else
				unification_source = get_value(unification_source);
		}
		else
			if (unification_target.type() == bound)
				unification_target = get_value(unification_target.bound_to());
		
		switch (unification_source.type())
		{
			case unbound:
				unification_source.bind_to(unification_target);
				*new_generator = &&unbind_source_var;
				goto new_generator_succeeded;
			case constant:
				if (unification_sourc!==unification_target)
					goto generator_failed_quickly;
				*new_generator = 1;
				goto new_generator_succeeded;
			
				
					
		}
	
	






invoked_rule_args_unification:
frame.generators[frame.depth] = get_unification_frame(frame.args[frame.depth], frame.locals[frame.depth]);
frame.depth += 1;
if (frame.depth < frame.args_len) goto invoked_rule_args_unification;
	have_incoming_existentials = false;
	for (int i = 0; i )

		have_incoming_existentials =
unification:
		source = unification_frame.source
		goto [unification_bind_source_var, unification_bind_source_const,
		unification_bind_source_list,
		]  [type(source)]

unification_bind_source_var:
		bind(frame.source, frame.target)
		frame.continue = unification_unbind_source
		goto frame.parent

unification_unbind_source:
		unbind(frame.source)
		goto frame




















		match_with_rules:
		current_body_triple = frame_body(frame)[frame.depth]
		rule = find_rule(current_body_triple);
	new_frame = get_new_frame(rule)
	new_frame.parent = frame

}










/*takes two things which may even be bound*/
get_value_multi(x,y)
{
	if (x.type() != bound)
		return TwoThings{x, get_value(y)};
	else
		x = x.bound_to();
	if (y.type() == bound)
		y = *y;
	if (x.type() == bound)
	{
		 if (y.type() == bound)
			 return get_value_multi(x,y);
		 return get_value(x), y;
	}
	return x, get_value(y);
}


















get_value_multi(x,y)
{
	if (x.type() == bound)
		x = *x;
	if (y.type() == bound)
		y = *y;
	if (x.type() == bound)
	{
		 if (y.type() == bound)
			 return get_value_multi(x,y);
		 return get_value(x), y;
	}
	return x, get_value(y);
}






get_value_multi_with_check(x,y)
{
	if (x.type() == bound)
		x = *x;
	if (y.type() == bound)
		y = *y;
	if (x.type() == bound)
	{
		 if (y.type() == bound)
			 return get_value_multi(x,y);
		 return get_value(x), y;
	}
	return x, get_value(y);
}







#define coroutine \
	char entry = 0;
void rule_unify(rule, args)
{
	frame = get_blank_frame(rule);
}
void query()
{
}





#ifdef memory_management_1
get_new_frame()
{
	fresh_frame = prepared_frames[rule].pop();
	frame_size = rule->frame_size;
	memcpy(fresh_frame, next_free_space, frame_size);
	prepared_frames[rule].put(next_free_space);
	next_free_space = next_free_space + frame_size
	return fresh_frame;
}

wrap_up()
{
	memcpy(prepared_frames[rule].peek(), finished_child_frame, rule->frame_size);
	prepared_frames[rule].prepend?(finished_child_frame);
}
#endif


class OneWord
{

};





unify:
	switch((unification_source.type() << 3) || unification_target.type())
	{
		case unification_bound_bound:
			unification_source,unification_target = get_value_multi(unification_source,unification_target);
			goto unify;
		case unification_bound_:
			unification_source,unification_target = get_value_multi(unification_source,unification_target);
			goto unify;


