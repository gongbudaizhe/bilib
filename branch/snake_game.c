/*
 * init_demo.c
 * Copyright (C) 2014 bily <bily@bily-Rev-1-0>
 *
 * Distributed under terms of the MIT license.
 */


#include<ncurses.h>     // 
#include<string.h>      // strlen
#include<unistd.h>      // usleep
#include<stdlib.h>      // malloc, free etc
#include<time.h>        // time
#include<pthread.h>     // multithreading

pthread_mutex_t lock;

typedef struct _BOX_struct{
    int startx, starty;
    int height, width;
    chtype content;
}BOX, * BOX_PTR;

typedef struct _Snake_struct{
    BOX* b;
    struct _Snake_struct* next;
}SNAKE_NODE, * SNAKE_PTR;

typedef struct{
    SNAKE_PTR head;
    SNAKE_PTR tail;
}SNAKE;

typedef struct{
    SNAKE* s;
    int forbidden_direction;
    int ch;
    bool gameover;
}GAME_STATE;


void init_BOX(BOX* b, int startx, int starty, int width, int height, chtype content);
void draw_BOX(BOX* b, bool flag);
void create_BOX(BOX** b, int startx, int starty);

bool check_dead(SNAKE* s, int startx_new, int starty_new);
int init_SNAKE(SNAKE** snake);
int push_SNAKE(SNAKE* snake, BOX* box);

chtype toogle_direction(chtype ch)
{
    switch(ch)
    {
        case KEY_UP:
            return KEY_DOWN;
        case KEY_DOWN:
            return KEY_UP;
        case KEY_LEFT:
            return KEY_RIGHT;
        case KEY_RIGHT:
            return KEY_LEFT;
        default:
            return -1;
    }
}

bool check_SNAKE(SNAKE* snake, int startx, int starty)
{
    SNAKE_PTR p = snake->head->next;
    while(p)
    {
        if(p->b->startx == startx && p->b->starty == starty)
            return TRUE;    
        p = p->next;
    }
    return FALSE;
}

bool check_dead(SNAKE *s, int startx_new, int starty_new)
{
    int startx, starty;
    startx = s->tail->b->startx;
    starty = s->tail->b->starty;

    if(startx > COLS - 2 || startx < 1 || starty > LINES - 2 - 2 || starty < 1) // crash the border
        return TRUE;
    if(check_SNAKE(s, startx_new, starty_new))
        return TRUE;
    return FALSE;
}

int make_FOOD(BOX** b, SNAKE*s)
{
    *b = (BOX*) malloc(sizeof(BOX));
    int startx,starty;

    // we don't want food to be placed in the snake
    while(TRUE)
    {
        startx = 2 * (rand() % (COLS / 2 - 2)) + 1;
        starty = rand() % (LINES - 2 - 2) + 1;
        if(!check_SNAKE(s, startx, starty))
            break;
    }
   
    (*b)->startx = startx;
    (*b)->starty = starty;
    (*b)->width = 2;
    (*b)->height = 1;
    (*b)->content = ' ' | A_REVERSE;
}

int init_SNAKE(SNAKE** snake)
{
    int i;
    int startx = 21;
    int starty = 10;
    int width = 2;

    BOX* b;
    SNAKE_PTR s;
    
    // first, we construct an empyt snake
    *snake = (SNAKE*) malloc(sizeof(SNAKE));
    (*snake)->head = (*snake)->tail = (SNAKE_PTR) malloc(sizeof(SNAKE_NODE));

    if(!(*snake)->head) return -1;
    (*snake)->head->next = NULL;

    // then, we enter some boxes
    for(i = 0; i < 5; i++)
    {
        // create box with reversed color
        create_BOX(&b, startx + width * i, starty);
        draw_BOX(b, TRUE);

        // push to snake
        push_SNAKE(*snake, b);
    }
    refresh();
}

int destroy_SNAKE(SNAKE* snake)
{
    while(snake->head)
    {
        snake->tail = snake->head->next;
        free(snake->head->b);
        free(snake->head);
        snake->head = snake->tail;
    }
}

int push_SNAKE(SNAKE* snake, BOX* box)
{
    SNAKE_PTR p = (SNAKE_PTR) malloc(sizeof(SNAKE_NODE));
    if(!p) return -1; // memory allocation failed

    p->b = box;
    p->next = NULL;
    snake->tail->next = p;
    snake->tail = p;
    return 0;
}

int pop_SNAKE(SNAKE* snake, BOX** b)
{
    SNAKE_PTR p;
    if(snake->head == snake->tail)
        return -1; // empty snake

    p = snake->head->next;
    snake->head->next = p->next;
    if(snake->tail == p) 
        snake->tail = snake->head;

    *b = p->b;
    free(p);
    
    return 0;
}

void move_SNAKE(SNAKE* snake, int startx, int starty)
{
    BOX* b;
    create_BOX(&b, startx, starty);
    draw_BOX(b, TRUE);
    push_SNAKE(snake, b);
    pop_SNAKE(snake, &b);
    draw_BOX(b, FALSE);
    free(b);
}


void create_BOX(BOX ** b, int startx, int starty)
{
    *b = (BOX*) malloc(sizeof(BOX));

    (*b)->startx = startx;
    (*b)->starty = starty;
    (*b)->width = 2;
    (*b)->height = 1;
    (*b)->content = ' ' | A_REVERSE;
}

void draw_BOX(BOX *p_box, bool flag)
{
    
    int i, j;
    int x,y,w,h;

    x = p_box->startx;
    y = p_box->starty;
    w = p_box->width;
    h = p_box->height;

    if(flag == TRUE){
        for(i = 0; i < w; i++)
            for(j = 0; j < h; j++)
                mvaddch(y + j, x + i, p_box->content);
    }
    else{
        for(i = 0; i < w; i++)
            for(j = 0; j < h; j++)
                mvaddch(y + j, x + i, ' ');
    }
    refresh();
}

void print_align_center(WINDOW *win, int row, char* words)
{
     int col = (COLS - strlen(words)) / 2;
     mvwprintw(win, row, col, words);    
}

void* threadFunc(void* arg)
{
    int startx,starty;
    bool is_dead = FALSE;
    bool eat_food;
    bool gameover;
    int forbidden_direction = KEY_LEFT;
    int ch;
    int score = 0;
    BOX * food;

    GAME_STATE* state = (GAME_STATE*) arg;
    
    make_FOOD(&food, state->s);
    draw_BOX(food, TRUE);

    while(TRUE)
    {
        // add mutex for ch and gameover since these will be read or write by two processes
        pthread_mutex_lock(&lock);
        startx = state->s->tail->b->startx;
        starty = state->s->tail->b->starty;
        ch = state->ch;
        gameover = state->gameover;
        pthread_mutex_unlock(&lock);

        if(ch == forbidden_direction)
            ch = toogle_direction(forbidden_direction);
        else
            forbidden_direction = toogle_direction(ch);

        switch(ch)
        {
        case KEY_UP:
            starty--;        
            break;
        case KEY_DOWN:
            starty++;
            break;
        case KEY_LEFT:
            startx -= 2;
            break;
        case KEY_RIGHT:
            startx += 2;
            break;
        default:
            break;
        }

        // if eat food then make new food
        if(startx == food->startx && starty == food->starty)
        {
            eat_food = TRUE;

            push_SNAKE(state->s, food);
            make_FOOD(&food, state->s);
            draw_BOX(food, TRUE);
            score++;
            mvprintw(LINES - 2, 9, "%i", score);
        }
        else
        {
            eat_food = FALSE;
        }

        if(!eat_food)
        {
            is_dead = check_dead(state->s, startx, starty);
            move_SNAKE(state->s, startx, starty); 
        }

        refresh();
        if(is_dead || gameover){
            pthread_mutex_lock(&lock);
            state->gameover = TRUE;
            pthread_mutex_unlock(&lock);
            break;
        }
        usleep(25000);
    }
}

int main(int argc, char** argv)
{
    int i;
    int j;
    int ch; 
    WINDOW* border_win;
    int startx, starty;
    bool is_dead; 
    SNAKE* s;

    // INITIALIZATION
    srand(time(NULL));

    // ncurses initialization
    initscr();              // start ncurses mode
    cbreak();               // diable line buffering
                            // differs with raw(). by cbreak(), we can get Ctrl+C etc working
    keypad(stdscr, TRUE);   // enable reading of function keys like F1,F2,arrow key,etc
    noecho();               // don't display what we type
    
    // draw border
    int height = 3;
    int width = 10;
    char* copyright = "BY BILY(gongbudaizhe@gmail.com)";
    mvprintw(LINES - 2, 3, "SCORE:0");
    mvprintw(LINES - 2, COLS - strlen(copyright), copyright);
    /*border_win = create_newwin(height, width, (LINES-height)/2, (COLS-width/2));*/

    refresh();
    border_win = newwin(LINES-2,COLS,0,0);
    box(border_win, 0, 0);
    wrefresh(border_win);

    // Welcome message
    print_align_center(stdscr, LINES / 2, "SNAKE GAME");
    print_align_center(stdscr, LINES / 2 + 1, "PRESS ANY KEY TO START");
    getch();
   
    print_align_center(stdscr, LINES / 2, "          ");
    print_align_center(stdscr, LINES / 2 + 1, "                      ");
    
    curs_set(FALSE); // we don't need blinking cursor now
    
    // GAME LOGIC
    init_SNAKE(&s);

    bool gameover;
    GAME_STATE state;
    state.s = s; 
    state.gameover = FALSE;
    state.ch = KEY_RIGHT;
    
    pthread_mutex_init(&lock, NULL);
    pthread_t pth;
    pthread_create(&pth, NULL, threadFunc, &state);
    
    while(TRUE)
    {
        ch = getch();        
        if(ch == 'q')
        {
            // exit game
            pthread_mutex_lock(&lock);
            state.gameover = TRUE;
            pthread_mutex_unlock(&lock);
            gameover = TRUE;
        }
        else{
            pthread_mutex_lock(&lock);
            state.ch = ch;
            gameover = state.gameover;
            pthread_mutex_unlock(&lock);
        }
        if(gameover)
            break;
    }
    
    pthread_join(pth, NULL);
    destroy_SNAKE(s);
    endwin();
    
    return 0;
}

