







void realloc()
{
        block_size += malloc_size;
        if (realloc(block, block_size) != block)
        {
            cerr << "cant expand memory" << endl;
            exit(1);
        }
}

size_t *grab_words(size_t count)
{
    size_t *result = (size_t *)first_free_byte;
    size_t increase = count * sizeof(size_t);
    //cerr << "block="<<block<<", requested " << count << "words="<<count * sizeof(size_t)<<"bytes, increase="<<increase<<",first_free_byte before = " << first_free_byte<<", after="<<first_free_byte + increase << ", must realloc:"<< (first_free_byte+increase >= block + block_size)<<endl;
    first_free_byte += increase;
    while (first_free_byte >= block + block_size)
        realloc();
    return result;
}

cpppred_state *grab_states(size_t count IF_TRACE_PROOF(cpppred_state *parent))
{
    auto r = (cpppred_state*) grab_words(count * sizeof(cpppred_state) / sizeof(size_t));
    #ifdef TRACE_PROOF
        for (size_t i = 0; i < count; i++)
            r[i].construct(parent);
    #endif
    return r;
}

void release_bytes(size_t count)
{
    #ifdef DEBUG
        for (size_t i = 1; i <= count; i++)
            *(first_free_byte - i) = 0;
    #endif
    first_free_byte -= count;
}

void release_states(size_t count)
{
    #ifdef TRACE_PROOF
        for (size_t i = 0; i < count; i++)
            (((cpppred_state*)first_free_byte)-i-1)->destruct();
    #endif
    release_bytes(count * sizeof(cpppred_state));
}

Thing *grab_things(size_t count)
{
    auto r = (Thing*) grab_words(count * sizeof(Thing) / sizeof(size_t));
    return r;
}

void release_things(size_t count)
{
    release_bytes(count * sizeof(Thing));
}

