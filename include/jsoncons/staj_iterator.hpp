// Copyright 2018 Daniel Parker
// Distributed under the Boost license, Version 1.0.
// (See accompanying file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

// See https://github.com/danielaparker/jsoncons for latest version

#ifndef JSONCONS_STAJ_ITERATOR_HPP
#define JSONCONS_STAJ_ITERATOR_HPP

#include <memory>
#include <string>
#include <stdexcept>
#include <system_error>
#include <ios>
#include <iterator> // std::input_iterator_tag
#include <jsoncons/json_exception.hpp>
#include <jsoncons/parse_error_handler.hpp>
#include <jsoncons/staj_reader.hpp>

namespace jsoncons {

template<class CharT, class T>
class basic_staj_array_iterator
{
    typedef CharT char_type;

    basic_staj_reader<char_type>* reader_;
    T value_;
public:
    typedef T value_type;
    typedef std::ptrdiff_t difference_type;
    typedef T* pointer;
    typedef T& reference;
    typedef std::input_iterator_tag iterator_category;

    basic_staj_array_iterator() noexcept
        : reader_(nullptr)
    {
    }

    basic_staj_array_iterator(basic_staj_reader<char_type>& reader)
        : reader_(std::addressof(reader))
    {
        if (reader_->current().event_type() == staj_event_type::begin_array)
        {
            next();
        }
        else
        {
            reader_ = nullptr;
        }
    }

    basic_staj_array_iterator(basic_staj_reader<char_type>& reader,
                        std::error_code& ec)
        : reader_(std::addressof(reader))
    {
        if (reader_->current().event_type() == staj_event_type::begin_array)
        {
            next(ec);
            if (ec)
            {
                reader_ = nullptr;
            }
        }
        else
        {
            reader_ = nullptr;
        }
    }

    const T& operator*() const
    {
        return value_;
    }

    const T* operator->() const
    {
        return &value_;
    }

    basic_staj_array_iterator& operator++()
    {
        next();
        return *this;
    }

    basic_staj_array_iterator& increment(std::error_code& ec)
    {
        next(ec);
        if (ec)
        {
            reader_ = nullptr;
        }
        return *this;
    }

    basic_staj_array_iterator operator++(int) // postfix increment
    {
        basic_staj_array_iterator temp(*this);
        next();
        return temp;
    }

    friend bool operator==(const basic_staj_array_iterator<CharT, T>& a, const basic_staj_array_iterator<CharT, T>& b)
    {
        return (!a.reader_ && !b.reader_)
            || (!a.reader_ && b.done())
            || (!b.reader_ && a.done());
    }

    friend bool operator!=(const basic_staj_array_iterator<CharT, T>& a, const basic_staj_array_iterator<CharT, T>& b)
    {
        return !(a == b);
    }

private:

    bool done() const
    {
        return reader_->done() || reader_->current().event_type() == staj_event_type::end_array;
    }

    void next();

    void next(std::error_code& ec);
};

template <class CharT, class T>
basic_staj_array_iterator<CharT, T> begin(basic_staj_array_iterator<CharT, T> iter) noexcept
{
    return iter;
}

template <class CharT, class T>
basic_staj_array_iterator<CharT, T> end(const basic_staj_array_iterator<CharT, T>&) noexcept
{
    return basic_staj_array_iterator<CharT, T>();
}

template<class CharT, class T>
class basic_staj_object_iterator
{
public:
    typedef CharT char_type;
    typedef std::basic_string<char_type> key_type;
    typedef std::pair<key_type,T> value_type;
    typedef std::ptrdiff_t difference_type;
    typedef value_type* pointer;
    typedef value_type& reference;
    typedef std::input_iterator_tag iterator_category;

private:
    basic_staj_reader<char_type>* reader_;
    value_type kv_;
public:

    basic_staj_object_iterator() noexcept
        : reader_(nullptr)
    {
    }

    basic_staj_object_iterator(basic_staj_reader<char_type>& reader)
        : reader_(std::addressof(reader))
    {
        if (reader_->current().event_type() == staj_event_type::begin_object)
        {
            next();
        }
        else
        {
            reader_ = nullptr;
        }
    }

    basic_staj_object_iterator(basic_staj_reader<char_type>& reader, 
                         std::error_code& ec)
        : reader_(std::addressof(reader))
    {
        if (reader_->current().event_type() == staj_event_type::begin_object)
        {
            next(ec);
            if (ec)
            {
                reader_ = nullptr;
            }
        }
        else
        {
            reader_ = nullptr;
        }
    }

    const value_type& operator*() const
    {
        return kv_;
    }

    const value_type* operator->() const
    {
        return &kv_;
    }

    basic_staj_object_iterator& operator++()
    {
        next();
        return *this;
    }

    basic_staj_object_iterator& increment(std::error_code& ec)
    {
        next(ec);
        if (ec)
        {
            reader_ = nullptr;
        }
        return *this;
    }

    basic_staj_object_iterator operator++(int) // postfix increment
    {
        basic_staj_object_iterator temp(*this);
        next();
        return temp;
    }

    friend bool operator==(const basic_staj_object_iterator<CharT,T>& a, const basic_staj_object_iterator<CharT,T>& b)
    {
        return (!a.reader_ && !b.reader_)
               || (!a.reader_ && b.done())
               || (!b.reader_ && a.done());
    }

    friend bool operator!=(const basic_staj_object_iterator<CharT,T>& a, const basic_staj_object_iterator<CharT,T>& b)
    {
        return !(a == b);
    }

private:

    bool done() const
    {
        return reader_->done() || reader_->current().event_type() == staj_event_type::end_object;
    }

    void next();

    void next(std::error_code& ec);
};

template <class CharT,class T>
basic_staj_object_iterator<CharT,T> begin(basic_staj_object_iterator<CharT,T> iter) noexcept
{
    return iter;
}

template <class CharT,class T>
basic_staj_object_iterator<CharT,T> end(const basic_staj_object_iterator<CharT,T>&) noexcept
{
    return basic_staj_object_iterator<CharT,T>();
}

template <class T>
using staj_array_iterator = basic_staj_array_iterator<char,T>;

template <class T>
using wstaj_array_iterator = basic_staj_array_iterator<wchar_t,T>;

template <class T>
using staj_object_iterator = basic_staj_object_iterator<char,T>;

template <class T>
using wstaj_object_iterator = basic_staj_object_iterator<wchar_t,T>;

#if !defined(JSONCONS_NO_DEPRECATED)

typedef staj_event_type stream_event_type;

template<class CharT>
using basic_stream_event = basic_staj_event<CharT>;

template<class CharT>
using basic_stream_reader = basic_staj_reader<CharT>;

template<class CharT>
using basic_stream_filter = basic_staj_filter<CharT>;

typedef basic_staj_event<char> stream_event;
typedef basic_staj_event<wchar_t> wstream_event;

typedef basic_staj_reader<char> stream_reader;
typedef basic_staj_reader<wchar_t> wstream_reader;

typedef basic_staj_filter<char> stream_filter;
typedef basic_staj_filter<wchar_t> wstream_filter;

#endif

}

#include <jsoncons/conversion_traits.hpp>

namespace jsoncons {

template<class CharT, class T>
void basic_staj_array_iterator<CharT,T>::next()
{
    if (!done())
    {
        reader_->next();
        if (!done())
        {
            decode_stream(*reader_, value_);
        }
    }
}

template<class CharT, class T>
void basic_staj_array_iterator<CharT,T>::next(std::error_code& ec)
{
    if (!done())
    {
        reader_->next(ec);
        if (ec)
        {
            return;
        }
        if (!done())
        {
            decode_stream(*reader_, value_, ec);
        }
    }
}

template<class CharT, class T>
void basic_staj_object_iterator<CharT,T>::next()
{
    reader_->next();
    if (!done())
    {
        JSONCONS_ASSERT(reader_->current().event_type() == staj_event_type::name);
        kv_.first =reader_->current(). template as<key_type>();
        reader_->next();
        if (!done())
        {
            decode_stream(*reader_, kv_.second);
        }
    }
}

template<class CharT, class T>
void basic_staj_object_iterator<CharT,T>::next(std::error_code& ec)
{
    reader_->next(ec);
    if (ec)
    {
        return;
    }
    if (!done())
    {
        JSONCONS_ASSERT(reader_->current().event_type() == staj_event_type::name);
        kv_.first =reader_->current(). template as<key_type>();
        reader_->next(ec);
        if (ec)
        {
            return;
        }
        if (!done())
        {
             decode_stream(*reader_, kv_.second, ec);
        }
    }
}

}

#endif

